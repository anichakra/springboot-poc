import base64

import cv2
import numpy as np
import torch
import torchreid
from sklearn.metrics.pairwise import cosine_similarity
from torch.nn import Linear
from torchvision import transforms
import logging
from framework import MessageProducer

logger = logging.getLogger("application")
color = (255, 20, 147)  # Pink bounding box

def preprocess_img(img):
    """
    Prepare an image for processing by applying transformations.

    This function takes an input image and applies a series of transformations including
    conversion to PIL format, resizing to a specific size expected by the model,
    conversion to a tensor, and normalization. The normalization step adjusts the color
    channel values to the distribution generally used for pre-trained models.

    Args:
        img: A tensor representing the input image to be preprocessed.

    Returns:
        A transformed image tensor, normalized and resized for further processing.
    """
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((256, 128)),  # Size expected by the model
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
        )
    ])
    return transform(img)

class ReidCallback:
    """
    Handles Re-Identification (ReID) and tracking of detected objects across frames.

    This class is responsible for managing embeddings of detected objects, assigning unique IDs based on
    cosine similarity, and preparing structured output messages for downstream systems. It initializes
    a pre-trained ReID model, maintains an ID database to track objects across frames, and works with a
    message producer to send tracking data to an outbound topic.
    """
    def __init__(self, producer:MessageProducer, outbound_topic, model, model_path, device):
        """
        Initializes the person re-identification (ReID) pipeline class with the necessary
        parameters, including a message producer, model, and device configuration. The
        constructor sets up the ReID model, loads pre-trained weights while excluding mismatched
        classifier parameters, and prepares the model for evaluation.

        Attributes:
        outbound_topic: str
            The topic to which outbound messages will be sent by the producer.
        id_database: dict
            A dictionary that stores person IDs and their corresponding embeddings.
        next_id: int
            A counter used to assign unique IDs to persons.
        reid_model: torch.nn.Module
            The person ReID neural network model instance.
        producer: MessageProducer
            The producer responsible for sending messages to the outbound topic.
        state_dict: dict
            The dictionary containing the model's parameters, loaded from a pre-trained file.

        Parameters:
        producer: MessageProducer
            Instance of a message producer to handle outbound messages.
        outbound_topic: str
            A string specifying the outbound topic for messages.
        model: str
            The name of the ReID model architecture to be instantiated.
        model_path: str
            Path to the file containing the pre-trained model's weights.
        device: str
            The device on which the model will operate (e.g., 'cpu' or 'cuda').
        """
        # Store previously seen person embeddings and IDs
        self.outbound_topic = outbound_topic
        self.id_database = {}  # Format: {id1: embedding_vector, id2: embedding_vector, ...}
        self.next_id = 0  # Counter for unique IDs
        # Initialize person ReID model
        self.reid_model = torchreid.models.build_model(
            name=model,  # You can choose available model architectures
            num_classes=751,  # Depends on the ReID system used
            pretrained=False
        )
        self.producer=producer
        # Load state dict ignoring weights of mismatched "classifier" layers
        self.state_dict = torch.load(model_path, map_location=torch.device(device))

        # Remove mismatched layers (classifier weights and bias)
        removed_params = ['classifier.weight', 'classifier.bias']
        for param in removed_params:
            if param in self.state_dict:
                del self.state_dict[param]

        # Load remaining parameters into the model
        self.reid_model.load_state_dict(self.state_dict, strict=False)
        #print("Model weights loaded, ignoring classifier parameters.")

        # Replace the classifier with a new layer, if needed
        # Example: If classification is required, redefine the classifier to match num_classes
        self.reid_model.classifier = Linear(in_features=512, out_features=751)  # 512 is last feature dim
        #print("Replaced classifier with a new output layer.")

        # Set the model to evaluation mode
        self.reid_model.eval()

    def callback(self, message):
        """
        Processes incoming messages, performs person re-identification, and publishes the results to an outbound topic.

        The callback function handles messages containing detection data and their corresponding frame. It performs person
        re-identification by generating embeddings for detected persons, matching these embeddings with an ID database, and
        assigning unique IDs. After processing, the function sends the re-identified results to a specified outbound topic.

        Parameters:
            message (dict): Incoming message containing the following keys:
                - 'frame': Base64-encoded string representing the frame image.
                - 'detections': List of detections in the frame, where each detection is represented as a dictionary.
                - 'frame_number' (int): Frame number for the current message.
                - 'frame_timestamp' (str): Timestamp associated with the frame.
                - 'frame_metadata' (dict): Metadata about the frame.
                - 'camera_metadata' (dict): Metadata about the camera capturing the frame.

        Raises:
            Exception: If an error occurs during message processing, handling, or publishing.
        """
        try:
            #time.sleep(1)

            frame = message['frame']
            detections = message['detections']

            # Decode base64 string to bytes
            frame_data = base64.b64decode(frame)
            # Convert bytes to numpy array
            frame_np = np.frombuffer(frame_data, dtype=np.uint8)
            # Decode image
            detected_frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)

            if not detections:
                return
                # Feed detections to the tracker
                # Step 1: Integrate ReID embeddings and assign unique IDs

            # Step 1: Generate embeddings for all detected persons
            embeddings = self.extract_embeddings(detected_frame, detections)

            # Step 2: Match persons in the current frame with database and assign IDs
            reid_results = self.match_and_assign_ids(embeddings, self.id_database)

            reid_message = {
                'frame_number': message['frame_number'],
                'frame_timestamp': message['frame_timestamp'],
                'frame': frame,
                'frame_metadata': message['frame_metadata'],
                'detections': reid_results,
                'camera_metadata': message['camera_metadata']
            }

            # Send message through the producer
            self.producer.produce_message(self.outbound_topic, reid_message)

        except Exception as e:
            logger.error ("Exception in consume_callback:", str(e))
            raise e

    def extract_embedding(self, img):
        """
        Extracts feature embedding from an input image using a pre-trained re-identification
        model. The image is processed and passed through the model to compute an embedding
        vector that represents the image's distinctive features.

        Parameters:
            img: The input image for which the feature embedding will be generated.

        Returns:
            ndarray: A flattened numpy array containing the feature embedding of the input
            image.
        """
        img_tensor = preprocess_img(img)
        with torch.no_grad():
            embedding = self.reid_model(img_tensor.unsqueeze(0))  # Forward pass
        return embedding.cpu().numpy().flatten()

    def extract_embeddings(self, detected_frame, detections):
        """
        Extracts embeddings for detected persons in a given frame.

        This method processes a list of detections, crops the corresponding person
        regions from the detected frame, and computes embeddings for each detected person
        region using a predefined function.

        Parameters:
            detected_frame: ndarray
                The frame/image in which people are detected and from which the regions
                corresponding to bounding boxes will be extracted.
            detections: list of dict
                A list of detections where each detection is a dictionary containing
                at least a 'bbox' key that holds the bounding box coordinates for
                a detected person in the format [x1, y1, x2, y2].

        Returns:
            list of dict
                A list of dictionaries where each dictionary contains:
                - detection: dict
                    The original detection data for a person.
                - embedding: ndarray
                    The computed ReID embedding vector for the corresponding person region.
        """
        embeddings = []
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']  # Bounding box of detected person
            person_image = detected_frame[y1:y2, x1:x2]  # Crop person region from the frame
            embedding = self.extract_embedding(person_image)  # ReID embedding extraction
            embeddings.append({'detection': detection, 'embedding': embedding})
        return embeddings

    def match_and_assign_ids(self, embeddings, id_database, sim_threshold=0.7):
        """
        Assign unique identifiers based on ReID embeddings by comparing with existing
        records in the ID database using cosine similarity. It assigns a pre-existing
        ID if the similarity exceeds a defined threshold or generates a new ID if no
        suitable match is found.

        Parameters:
        embeddings : list[dict]
            A list of dictionaries where each dictionary contains 'embedding', and a
            corresponding detection dictionary with bounding box (`bbox`), score
            (`score`), and class (`class`).
        id_database : dict[str, numpy.ndarray]
            A dictionary with existing person IDs as keys and their ReID embeddings
            as values.
        sim_threshold : float, optional
            A similarity threshold for matching embeddings (default is 0.7).

        Returns:
        list[dict]
            A list of dictionaries where each dictionary contains the assigned 'id',
            'embedding', bounding box (`bbox`), detection score (`score`), detected
            class (`class`), similarity match score (`similarity`), and additional
            attributes like 'color'.

        Raises:
        None
        """
        results = []

        for em in embeddings:
            embedding = em['embedding']  # Current person's ReID embedding
            bbox = em['detection']['bbox']
            score = em['detection']['score']
            clazz = em['detection']['class']
            assigned_id = None
            max_sim = 0

            # Compare with every stored embedding in the ID database using cosine similarity
            for person_id, existing_embedding in id_database.items():
                similarity = cosine_similarity(embedding.reshape(1, -1), existing_embedding.reshape(1, -1))[0][0]
                if similarity > sim_threshold and similarity > max_sim:
                    max_sim = similarity
                    assigned_id = person_id

            # If a match is found, assign the same ID
            if assigned_id is not None:
                results.append({'id': assigned_id, 'embedding': embedding, 'bbox': bbox, 'score': score, 'class': clazz,
                                'similarity': max_sim, 'color': color})
            else:
                # Otherwise, assign a new unique ID and add the embedding to the database
                assigned_id = self.next_id
                self.id_database[assigned_id] = embedding
                self.next_id += 1
                results.append({'id': assigned_id, 'embedding': embedding, 'bbox': bbox, 'score': score, 'class': clazz,
                                'similarity': None, 'color': color})

        return results
