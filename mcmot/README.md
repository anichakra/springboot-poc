# Scalable MCMOT

## Overview
This project demonstrates how to scale any computer vision module using Multi-Camera Multi-Object Tracking (MCMOT) as an use-case. The MCMOT application has six computer vision modules: `capture`, `detection`, `reid`, `tracker`, `unification` and `analytics`.

### Description

Scalable MCMOT provides an innovative solution for balancing accuracy and FPS (Frames per Second) by replicating and scaling computer vision modules. The project uses a timestamp-based frame-synchronization algorithm to ensure seamless processing of frames. 

The architecture is powered by **Apache Kafka**, enabling highly scalable frame processing. Modules are designed with modularity in mind and can be executed independently but follow a sequential dependency chain: 
`Capture -> Detection -> ReID -> Tracker -> Unification`.

Key steps include:
1. **Frame capture**: Captures video streams or processes offline videos and publishes the frames to Kafka topics.
2. **Sequential module execution**: The frames are consumed by `Detection`, `ReID`, and `Tracker` modules for further processing.
3. **Unification**: Synchronizes frames across multiple cameras using the frame-synchronization algorithm.

### Features

- Innovative **timestamp-based frame-synchronization** algorithm to balance between throughput and accuracy.
- Scalable architecture using **Kafka** for robust frame processing from multiple cameras.
- Modular design with five key components: `capture`, `detection`, `reid`, `tracker`, and `unification`.
- Ability to process both **streaming** and **offline** video sources.
- Adjustable settings for **frame synchronization** parameters to customize behavior for various use cases.
  
### Pipeline

The order in which each module must be placed:

1. **Capture**: Reads from a particular video file and streams frames to a Kafka topic. Sample videos are stored in the
   `capture/video` directory. Each capture instance processes frames from one video file. For multiple camera feeds,
   multiple videos are used, requiring multiple capture instances to be started.

2. **Detection**: Detects objects in each frame.

3. **ReID**: Creates embeddings by cropping each detected object with the ReID identifier.

4. **Tracker**: Creates a tracking ID for each detected person. The tracker can take input frames from either the ReID
   or Detection module directly. It can also take frames directly from the Capture module and use a Kalman filter to
   predict tracking, especially when frames are not detected during synchronization. Each tracker instance is linked to
   a specific camera or capture instance.

5. **Unification**: Unifies the tracker output from multiple captures and creates a combined frame for each instance of
   time from all the camera-captured videos, synchronized with timestamps. It also generates a video with synchronized
   frames.

6. **Analytics**: Uses a multi-modal LLM to create an inferencing log based on combined and synchronized frames from all
   camera captures.

### Technologies Used

#### **Key Dependencies**
The `dependencies` section lists several critical libraries that provide the foundation for the project's functionality. These are categorized by their primary use cases:
##### 1) **Computer Vision and Object Tracking**
- **`opencv-python`**:
The OpenCV library is critical for video and image processing tasks like reading camera streams, manipulating frames, and visualizing results.
- **`ultralytics`**:
This package likely provides **YOLO-based object detection**. YOLO (You Only Look Once) is a state-of-the-art deep learning model for real-time object detection.
- **`torch`** and **`torchreid`**:
    - `torch` refers to PyTorch, a deep learning library that serves as the backbone for training models and running inference.
    - `torchreid` is likely used for object re-identification (ReID), enabling the system to distinguish and track objects—even the same object appearing in different camera frames.

- **`deep-sort-realtime`**:
This package provides the **Deep SORT tracking algorithm**, which combines detection-based tracking with ReID embeddings to track objects in real-time across frames.

##### 2) **Kalman Filtering and Statistical Models**
- **`pykalman`**:
Implements Kalman filtering, which is essential for predicting the movement of objects between detections and for smoothing results from object trackers.

##### 3) **Machine Learning and Data Processing**
- **`scikit-learn`**:
A general-purpose machine learning toolkit that could support clustering, preprocessing, or models for additional tasks. Functions like PCA, k-means clustering, or evaluation metrics might also be part of the project.

##### 4) **Output and Reporting Tools**
- **`openpyxl`**:
A library that enables working with Excel files, likely for exporting tracking results, logs, or additional data analysis.
- **`tensorboard`**:
Used for visualizing performance metrics, model learning, and debugging. It integrates seamlessly with PyTorch and allows monitoring during model training or runtime.

##### 5) **Data Integration and Loading**
- **`gdown`**:
Facilitates the downloading of data or pre-trained models directly from shared Google Drive links.
- **`kafka-python-ng`**:
Provides a Python client for **Apache Kafka**, enabling the system to handle streaming data pipelines, which are critical for multi-camera systems that collect high-volume, real-time data.

##### 6) **Natural Language Processing (NLP) and Frameworks**
- **`langchain-ollama`, `langchain-core`, `langchain-openai`**:
These dependencies suggest some use of Language Chain frameworks to interact with large language models (e.g., OpenAI APIs). While their specific role isn't fully clear from this file, they may enable advanced functionality like automated configuration, logging explanations, or metadata management.
- **`ollama`**:
Likely facilitates interactions with models hosted locally (or through an organization-provided infrastructure), complementing the LangChain framework.

##### 7) **Data Validation**
- **`pydantic`** and **`pydantic-core`**:
These libraries provide robust data validation functionality and model structuring, ensuring that the input/output is well-validated and adheres to the expected structure. This is useful for handling complex data flows in the tracking pipeline.

#### **Build System**
- **Build Tool**:
The project uses **Poetry** for dependency management and packaging. Specifically, the core library for build management (`poetry-core`) is employed via the backend API `poetry.core.masonry.api`.
Poetry simplifies the declaration and installation of dependencies and ensures reproducibility in the project's environment.
- **Version Constraint**:
The Poetry core version is capped between 2.0.0 and 3.0.0, ensuring compatibility with the backend.

#### **Highlights of Scalability**
- **Multi-Camera Input**: The dependency on Kafka indicates the system is designed to handle a large amount of streaming data across multiple cameras, making it scalable for real-world deployments.
- **Modular Architecture**: By segmenting responsibilities into `capture`, `detection`, `reid`, `tracker`, and `unification`, the project demonstrates easy extendability and maintenance through modular design.
- **Advanced Modeling and Real-Time Capability**: The integration of libraries like PyTorch, Deep SORT, and YOLO show that the project aims to provide real-time computer vision solutions at scale.

## Quick Start

### Prerequisite
Although this application must be running on a distributed system, it can still be run in standalone mode on a single
machine for demonstration purposes. This project is tested in **Python 3.12** on an **M3 Pro MacBook Pro**. To set it
up, ensure Python is installed with the same version on a **GPU-based Linux system** with at least **16 GB Memory** and
**8 CPUs**. Follow these steps:

1. First, download and set up **Apache Kafka**. Refer to
   the [Kafka Quickstart Guide](https://kafka.apache.org/quickstart). Use the latest Kafka (without zookeeper) and run the following commands from the home directory of where kafka is installed.
```bash
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/server.properties
bin/kafka-server-start.sh config/server.properties

```
2. Create the Kafka topics using the `setup.py` module.
3. Navigate to the **mcmot** directory (project directory) and check all the JSON configuration files under the `config`
   directory.
4. Create .venv folder inside mcmot. Refer to https://docs.python.org/3/library/venv.html
5. Install poetry by running `pipx install poetry` or `pip install poetry` from mcmot. 
6. Then install all dependencies using `poetry install`
7. Create two sub-directories in mcmot directory - logs and pids
8. Run the following aggregated commands to start the MCMOT pipeline:

```bash
   PYTHONPATH=. \
   poetry run python setup.py config/setup-single-config.json && \
   poetry run python start.py config/pipeline-single-nosync-config.json && \
   poetry run python main.py '{"pipeline": "test", "signal": "START"}'
```

This will run the computer-vision (CV) pipeline for a single camera capture with only detection and tracker without any frame synchronization.
Note: If this aggregated command is not working in the OS, then run these 4 commands separately in the same sequence. 

#### Explanation of the Commands

1. **Set Up Kafka Topics**:  
   Initializes Kafka topics as configured in the `setup-single-config.json` file.

2. **Start the Pipeline**:  
   Starts all the computer vision modules (e.g., capture, detection, tracker) as configured in
   the `pipeline-single-config.json` file.

3. **Trigger the Pipeline**:
   Executes the pipeline by sending the `START` signal with the specified configuration.

On start 3 Open-CV based python windows will open-up that will show observability of capture, detection and tracker modules.

#### Remove Existing Output Directory
   Check beforehand that you have deleted the output directory inside mcmot beforehand. The output directory is created by any prior run of Unification module.

#### How to terminate
After everything has run perfectly, check the mcmot/output folder for the synchronized frames and the synchronized frame video. Along with that we will find the unified.log and unified.xls containing the LLM output.
To stop all the processes simply run the following command:

```bash
PYTHONPATH=. poetry run python stop.py
```

#### With Frame-synchronization
The same pipeline can be run with frame-synchronization, so that we can understand the difference happening. Frame synchronization will solve the problem of delay in processing each frame by detection module, by intelligently skipping frames in between.

```bash
   PYTHONPATH=. \
   poetry run python setup.py config/setup-single-config.json && \
   poetry run python start.py config/pipeline-single-config.json && \
   poetry run python main.py '{"pipeline": "test", "signal": "START"}'
```

#### With Multiple Camera Captures

This next commands will start multiple camera MCMOT pipeline with all the computer-vision (CV) modules in the same machine with all the modules.

With 2 cameras:
   ```bash
   PYTHONPATH=. \
   poetry run python setup.py config/setup-multi-config.json && \
   poetry run python start.py config/pipeline-dual-config.json && \
   poetry run python main.py '{"pipeline": "test", "signal": "START"}'
   ```
With 4 cameras:
   ```bash
   PYTHONPATH=. \
   poetry run python setup.py config/setup-multi-config.json && \
   poetry run python start.py config/pipeline-multi-config.json && \
   poetry run python main.py '{"pipeline": "test", "signal": "START"}'
   ```
This will run capture->detection->reid->tracker->unification->analytics. Here 4 python windows will open up to show the capture, detection, reid and tracker output frames.

Each time the pipeline has to be rerun, make sure to stop the previous pipeline using the stop.py module.

## Setup Module

### Overview

The setup.py module creates the necessary topics in kafka required for the pipeline. Check the setup-config.json file. Each pipeline has a name and related kafka brokers along with list of topics required for each module. Each topic pertaining to each module must specify number of partitions required. The topics are named after the module that publishes the message into it. The topics are outbound only for a module. For example capture module will write to a topic called capture-test-topic where test is the name of the pipeline. From capture-test-topic detection module will poll frames and creates detection boxes and publish the same to the detection-test-topic. 
If the pipeline scalability changes then the setup has to be recreated, otherwise not. The setup clears the pipeline setup with all topics and recreates everything again. To run setup:

---

### Configuration Layout

- `"pipeline"`: Unique name for the computer vision pipeline (e.g., `test`).
- `"bootstrap-servers"`: Kafka cluster configuration. This is optional for localhost-based default settings.
- `"topics"`: Suffix of the topics with partition. A topic with name <module-name>-<pipeline-name>-topic will be created for each module where the module will publish message containing frame number, frame timestamp, binary frame, frame metadata and camera metadata. The example shows the partitions to create 2 partitions in the outbound kafka topic for capture, and 5 partitions in the outbound kafka topic for detection, so that we can run 2 processes of detection and 5 processes of reid.

---

### How to Run

```bash
PYTHONPATH=. poetry run python setup.py config/setup-config.json
```

Instead of passing the setup-config.json one can also provide the configuration inline also:

```bash
PYTHONPATH=. poetry run python setup.py '{
  "pipeline": "test",
  "bootstrap-servers": [
    "localhost:9092"
  ],
  "topics": {
    "capture": 2,
    "detection": 5,
    "reid": 1,
    "tracker": 1,
    "unification": 1
  }
}'
```
The process terminates after the required topics are created.

## Start Module

### Overview
The start.py module will start all the cv modules that are configured in the pipeline-config.json. The `start.py` module serves as the central script for starting and managing various components of the system. It simplifies the process of launching multiple modules, handling their logging, and ensuring proper cleanup in case of failures.

---

### What it Does
1. **Starts Module Processes**:
    - Launches all specified modules based on a configuration file.
    - Supports running multiple instances of a module for scalability.

2. **Manages Observability**:
    - Optionally starts observability processes for modules to monitor their activity.

3. **Handles Errors Gracefully**:
    - If any issues occur during startup, it safely stops all the running processes to avoid resource waste.

4. **Organizes Logs and Tracking**:
    - Ensures each module has its own log file and process ID (PID) for easy monitoring and management.

---

### **Configuration Layout**

The configuration is a list of module objects, where each object defines the following parameters:
1. **`name`**:
The name of the module to be initialized (e.g., `capture`, `detection`, `analytics`).
2. **`observability`** (_optional, boolean_):
Whether an observability process should be started for the module.
    - `true`: Enables observability for the module.
    - `false`: Observability is disabled (default if not specified).

3. **`config`**:
The configuration data for the module. It can be either of:
    - A JSON object for inline configurations.
    - A string pointing to an external JSON file containing the configuration.
Check below sections to know more about individual module configuration.

4. **`replication-factor`** (_optional, integer_):
The number of replicated instances of a module to be launched.
    - Default: `1` (not replicated unless specified).

---

### How to Run
- Reads configuration data for the modules to initialize.
- Starts required module instances and their observability processes, as defined in the configuration.
- Automatically creates needed directories for logs and process tracking.
- Cleans up processes in case of errors.

The following script will start all the cv modules mentioned in the pipeline-config.json:

```bash
PYTHONPATH=. poetry run python start.py config/pipeline-config.json
```
The configuration can be also provided inline, but most of the time it will be large so better to create a configuration file and use it.The process terminates after all the module processes are started in the background. We can use `ps -ef | grep _init.py` to check the module processes. The module processes will be waiting for main.py to send signal to start processing the video frames.

## Main Module

### Overview

After starting all the modules the video processing will not automatically start. 
The read of video file by capture module will start when trigger through a signal. 
The `main.py` script is designed to configure, prepare, and send data messages to a specified Kafka topic. 
It serves as the entry point to run the application logic, leveraging robust logging and error-handling mechanisms to ensure proper operation and cleanup during execution.
---

### Features

1 **Data Processing and Message Construction**:
- Constructs a message using the signal and loop count provided in the configuration.
- Dynamically determines the Kafka topic based on the provided pipeline name.

2 **Message Production to Kafka**:
- Sends the constructed message to the specified Kafka topic via the `MessageProducer` class. 
- The message is passed to a dynamic topic called: camera-<pipeline-name>-topic. This is the inbound topic for the capture module.

3 **Signal-Based Control**:
Users interact with the system via **signals**:
- **Start Signal (`START`)**: Begins processing frames. The system reads frames from the source, applies any synchronization logic, and publishes the processed data to an outbound topic.
- **Stop Signal (`STOP`)**: Halts frame processing gracefully. Any in-progress tasks are finalized.
- **Hold Signal (`HOLD`)**: Pauses operations temporarily, retaining the processing state.
- **Resume Signal (`RESUME`)**: Allows the system to continue processing from where it was paused.

---

### Usage
1. Ensure the required Kafka server(s) are active and accessible.
2. Place the configuration file or provide necessary arguments for:
    - `pipeline` (e.g., the name of the processing pipeline).
    - `signal` (e.g., data to be transmitted).
    - `loop-count` (default: 1).
    - `bootstrap-servers` (default: `["localhost:9092"]`).

---

### How to Run

To run main.py we have send the signal and the loop-count inline or through a configuration file.

```bash
PYTHONPATH=. poetry run python main.py '{"pipeline": "test", "signal": "START"}'     
```

Provide different other signals to test.

## Stop Module


### Overview

When the start.py is called, all the CV modules starts and their process pid is stored in mcmot/pids directory. The stop process reclaims all the processes running referring to this directory. 

---

### How It Works
#### **1. Stopping Processes Using PID Files**
- The module looks for `.pid` files in a specified directory (default: `./pids`).
- For each PID listed in the files:
    - It verifies if the process is still running.
    - Sends the `SIGTERM` signal to terminate the process cleanly.
    - If the process doesn’t terminate within the allowed time, it sends a `SIGKILL` signal to force termination.

- Successfully terminates processes and cleans up the corresponding `.pid` files.

#### **2. Stopping Processes by Matching Keywords**
- If `.pid` files are missing or incomplete, the module searches for processes with names or command-line arguments containing specific keywords (e.g., `"capture_init.py"`, `"observability_init.py"`).
- It terminates matching processes similarly, first gracefully and, if needed, forcefully.

---

### How to Run

The stop.py is run by:
```bash
PYTHONPATH=. poetry run python stop.py
```

This will terminate all the CV module processes running including observability.

## Frame Synchronization Module

### Overview
The **Frame Synchronization Module** is responsible for aligning frames from multiple video sources (e.g., cameras) based on either **frame numbers** or **timestamps**. This ensures that frames from different sources are consistently synchronized for downstream operations such as multi-object tracking, scene reconstruction, or real-time video analysis.
This module is part of the mcmot/framework and is predominantly used by the framework's Event module.
The module uses configurable synchronization settings to adapt to various real-time or batch-processing requirements. It also handles delays, buffering, and variations in input rates, making it ideal for distributed and scalable systems.

---

### Features
The Frame Synchronization Module is a robust solution for aligning frames across multiple video sources with configurable settings for different use cases. Its scalable architecture, dynamic synchronization modes, and efficient retention management make it ideal for real-time or batch systems requiring precise frame alignment.

- **Dynamic Synchronization Types**:
  - Synchronize based on `frame numbers` or `timestamps`.
- **Tolerance-based Grouping**:
  - Adjustable sync tolerance calculated automatically from the frames per second (FPS).
- **Thread Safety**:
  - Concurrency control using thread locks for seamless multi-camera operation.
- **Retention and Buffer Management**:
  - Configurable memory cleanup for old and ungrouped frames.
- **Advanced Frame Handling**:
  - Automatically determines whether to **skip frames** or **wait** for delayed frames based on latency thresholds.
- **Callback-Driven Processing**:
  - Allows custom user-defined callbacks for processing synchronized frames.
- **Scalable Architecture**:
  - Designed for distributed video systems using minimal resources.

---

### FrameSyncService
The main interface for frame synchronization. This service dynamically chooses:
- **FrameSyncNumberService**: For number-based synchronization.
- **FrameSyncTimestampService**: For timestamp-based synchronization.

It provides the following methods:
- **`collect(frame_number, frame_timestamp, fps, camera_id, **kwargs)`**:
  Collects frame data from cameras and buffers it for synchronization.
- **`synchronize(callback)`**:
  Groups synchronized frames and processes them using the provided callback. This does the multiple camera synchronization.
- **`skip_or_wait(camera_id)`**:
  Determines whether frames for a specific camera should be skipped or delayed. This is single camera synchronization.

---

### FrameSyncNumberService
Synchronizes frames based on their sequential **frame numbers**. It matches frame numbers from multiple cameras to group them for downstream processing.

Key responsibilities:
- Buffers frame metadata and groups frames by identical frame numbers.
- Cleans up unprocessed frames exceeding the retention time.
- Skips or delays frames based on their arrival sequence.

---

### FrameSyncTimestampService
Synchronizes frames based on their **timestamps**, particularly useful for real-time systems with dynamic or inconsistent frame numbers.

Key responsibilities:
- Groups frames based on timestamp tolerance (calculated as `1 / fps`).
- Skips or delays frames based on latency thresholds and retention times.
- Ensures grouped frames are processed in the correct order via callbacks.

---

### FrameSyncConfiguration
The **Frame-Sync Configuration** ensures the efficient synchronization of frames across multiple cameras or sources in scenarios where real-time or batch processing is required. The given configuration is implemented using the `FrameSyncConfiguration` class, which provides a set of parameters to control synchronization behavior, backlog handling, retention policies, and frame processing logic.
Below is a detailed explanation of the configuration attributes, their behavior, and how they are incorporated into the Computer Vision (CV) module's startup process.
The following are the attributes of the `frame-sync` configuration, describing each in detail with their purpose, use cases, and how they affect frame synchronization.

#### **1. `backlog_threshold` (int)**
- **Description**: Sets the maximum number of unsynchronized frames allowed in the buffer before triggering synchronization. Frames exceeding this threshold may delay the synchronization process or get discarded.
- **Default**: `0` (no backlog limit).
- **Validation**: Must be `>= 0`. If `0`, backlog handling is effectively disabled.
- **Role**:
    - Limits the memory usage by capping the number of frames retained in the buffer.
    - Ensures synchronization begins promptly when a backlog of frames is detected.

- **Use Case**: Set this higher in systems with high variability in frame arrival times to allow for buffering, but balance with system memory constraints.

#### **2. `backlog_check_interval` (float)**
- **Description**: Specifies the interval, in seconds, at which the backlog is checked. Controls how frequently the system evaluates the buffered frames against the backlog threshold.
- **Default**: `0.0` (disables periodic backlog checks).
- **Validation**: Must be `>= 0`. A nonzero value ensures periodic checks to limit buffering and memory usage.
- **Role**:
    - Ensures effective backlog management by regularly validating buffer size.
    - Reduces latency by triggering synchronization as soon as the threshold is breached.

- **Use Case**: Larger intervals reduce processing overhead, while smaller intervals ensure tighter control over buffered frames.

#### **3. `frame_sync_type` (str)**
- **Description**: Defines the method of synchronization. Frames can be synchronized using their **timestamps**, **frame numbers**, or a combination of both.
- **Accepted Values**:
    - `timestamp`: Synchronization based on the real-world time each frame was captured.
    - `number`: Synchronization using sequential frame numbers.
    - `None`: Indicates no specific synchronization logic.

- **Default**: `None`.
- **Validation**: Must be one of `{"timestamp", "number", None}`.
- **Role**:
    - For real-time streams, `"timestamp"` is preferred as it ensures alignment based on time differences.
    - For pre-recorded videos or consistent streams, `"number"` is often used since frame numbers are inherently aligned.

- **Use Case**: Systems with variable frame rates or high latency benefit from timestamp-based synchronization. Number-based synchronization is suitable for scenarios where frame order is already guaranteed.

#### **4. `fps` (int)**
- **Description**: Indicates the frames-per-second value that guides the synchronization process. When set to `0`, the FPS specified in the frame's metadata will take precedence.
- **Default**: `0`.
- **Validation**: Must be `>= 0`. A value of `0` means synchronization relies on the frame metadata.
- **Role**:
    - Provides an optional way to override frame metadata with a fixed FPS for consistent synchronization.
    - Helps calculate timestamp tolerances when the metadata doesn't include FPS.

- **Use Case**: Used for streams without reliable frame metadata or for enforcing a fixed FPS across heterogeneous sources.

#### **5. `retention_time` (float)**
- **Description**: Specifies the maximum time (in seconds) a group of frames can remain in the synchronization buffer while waiting for other frames to arrive. After this time, unsynchronized frames are discarded. Old and ungrouped frames exceeding the configured retention time are automatically cleaned. Ensures memory efficiency and prevents old data from clogging the buffers.
- **Default**: `60.0`.
- **Validation**: Must be `> 0`.
- **Role**:
    - Prevents the buffer from retaining unprocessable groups indefinitely, reducing memory overhead.
    - Controls how long the system waits for missing frames to arrive.

- **Use Case**: In high-latency or low-frequency systems, a longer retention time can avoid unnecessary frame discards.

#### **6. `latency_threshold` (float)**
- **Description**: The maximum allowable latency (in seconds) for synchronization. Defines how much delay is tolerable for processing frames.
- **Default**: `60.0`.
- **Validation**: Must be `>= 0`.
- **Role**:
    - Protects processing pipelines from accumulating excessive delays.
    - Skips frames that fall outside the maximum latency window.

- **Use Case**: Used in performance-critical systems where processing delays must be minimized.

#### **7. `ignore_initial_delay` (bool)**
- **Description**: Determines whether the initial frame delay during startup should be ignored.
- **Default**: `False`.
- **Validation**: If `True`, at least one of `backlog_threshold` or `backlog_check_interval` must be provided.
- **Role**:
    - Skips initial checks and processes immediately starting frames, allowing faster startup when some frames can be missed.

- **Use Case**: Useful for applications where capturing the latest frames quickly is more important than strict synchronization from the start.

#### **8. `enable_sequencing` (bool)**
- **Description**: Enables sequencing of frames before synchronization. Ensures frames from each source are ordered correctly (by timestamp or number) before synchronization.
- **Default**: `False`.
- **Role**:
    - Ensures that frames are correctly ordered before synchronization, even if they arrive out of sequence.

- **Use Case**: Used when frame sources are known to provide unordered frames.

#### **9. `seek_to_end` (bool)**
- **Description**: Forces synchronization to process only the most recent frame in the input queue, ignoring all previous frames.
- **Default**: `False`.
- **Validation**: Overrides other configurations such as `retention_time`.
- **Role**:
    - Eliminates latency by always processing the latest available frame.
    - Ideal for applications focusing on real-time performance rather than full-frame synchronization.

- **Use Case**: Useful in live camera feeds where real-time frame processing is critical.

#### **10. `unify` (bool)**
- **Description**: Groups frames from different sources into a unified set during synchronization.
- **Default**: `False`.
- **Role**:
    - Combines frames from multiple cameras into a single synchronized group.
    - Passes grouped frames to the CV module's callback.

- **Use Case**: Essential for multi-camera setups where synchronized frames are jointly analyzed.

---

### How This Configuration is Passed to the CV Module
The configuration is passed to the CV module during its initialization process to ensure proper synchronization. Here's an overview of how it is set up and its flow:
1. **Configuration Parsing**: The `frame-sync` object is typically loaded as a JSON configuration. Each attribute is validated and mapped to the corresponding parameter in the `FrameSyncConfiguration` class.
2. **Object Initialization**: The `FrameSyncConfiguration` object is constructed with validated parameters. Any missing or invalid values are replaced with defaults, ensuring robustness.
3. **Incorporation into Frame Sync Services**:
    - The configuration object is passed to the **FrameSyncService**, which sets up the synchronization backend (`timestamp` or `number`) as per the `frame_sync_type`.
    - Additional parameters (e.g., backlog settings, retention time, latency thresholds) guide how frames are buffered, grouped, and synchronized.

4. **Integration with the CV Pipeline**: The frame-sync service is further incorporated into the CV module pipeline, managing incoming frames and providing synchronized groups to the module's callback for processing.
5. **Dynamic Behavior**: Attributes such as `seek_to_end`, `ignore_initial_delay`, and `unify` dynamically adapt processing behavior to meet the application's specific requirements.

The `frame-sync` configuration that goes with the module configuration, provides full control over frame synchronization, allowing flexibility and robustness in multi-source or multi-camera setups. Attributes such as `backlog_threshold`, `retention_time`, `fps`, and `frame_sync_type` define how frames are grouped while ensuring minimal latency and efficient memory usage. By integrating this configuration into the CV module's startup and synchronization services, the system ensures seamless, responsive, and accurate frame processing for various computer vision applications.

---

### Core Features Explained

1. **Dynamic Synchronization**:
   - Depending on `frame_sync_type` in the configuration, the module switches between number-based and timestamp-based synchronization.

2. **Skip or Wait Decisions**:
   - **Skip**: If a frame arrives after the expected sequence or timestamp, older delayed frames are skipped.
   - **Wait**: If incoming frames are slightly delayed but expected soon, the system waits instead of skipping.

3. **Retention Cleanup**:
   - Unprocessed or delayed frames exceeding the retention time are automatically removed to prevent memory overload.

4. **Callback Integration**:
   - Enables users to define their custom logic to process synchronized frames.


## Event Module

### Overview
The Event Module provides seamless integration with Apache Kafka for producing and consuming messages. It is designed for real-time streaming systems, offering features like advanced synchronization, backlog management, and user-defined processing logic. The primary components of this module are `MessageProducer` and `MessageConsumer`, which streamline Kafka interactions while maintaining flexibility and scalability. The Event Module, with its `MessageProducer` and `MessageConsumer` components, provides a powerful and flexible framework for interacting with Apache Kafka. Its advanced features, such as message routing, synchronization, sequencing, and backlog management, make it ideal for building scalable, real-time data processing pipelines. Its robust error handling and performance tracking ensure reliability and transparency in streaming workflows.

---

### MessageProducer

The `MessageProducer` class is responsible for creating topics and producing messages to Kafka. It simplifies Kafka topic management and ensures reliable message delivery.

#### Key Features:
- **Message Production**:
  - Produces messages to specified Kafka topics.
  - Supports partitioning with customizable keys for efficient routing.
- **Topic Management**:
  - Enables creation and deletion of Kafka topics.
  - Configurable partition and replication settings during topic creation.
- **Custom Serialization**:
  - Handles serialization of complex Python objects (e.g., NumPy arrays) using a JSON-based serializer.
- **Delivery Monitoring**:
  - Logs message delivery details, such as the topic, partition, and offset.

#### Benefits:
- Simplifies Kafka topic and message management.
- Enables partition-based routing for efficient load balancing.
- Easily handles large, complex data types with a custom serializer.
- Provides real-time monitoring of message delivery.

---

### MessageConsumer

The `MessageConsumer` class is designed for robust and efficient message consumption from Kafka topics. It supports features like frame synchronization, message sequencing, and backlog management for processing streaming data.

#### Key Features:
- **Stream Consumption**:
  - Consumes messages from Kafka topics using specified group IDs.
  - Supports user-defined callbacks for processing each message.
- **Frame Synchronization**:
  - Aligns and synchronizes frames using `FrameSyncService`, ensuring proper processing of frames from single or multiple sources.
- **Message Sequencing**:
  - Ensures messages arriving out of order are correctly sequenced before processing.
- **Backlog Management**:
  - Dynamically monitors and processes accumulated backlogged messages to maintain low-latency streaming.
- **Performance Monitoring**:
  - Logs processing times, frame rates, and backlog metrics.

#### Benefits:
- Simplifies real-time message consumption.
- Ensures proper alignment and sequencing of data in multi-camera or multi-source systems.
- Provides real-time backlog handling to avoid delays.
- Offers flexibility for custom logic through user-defined callbacks.

---

### Error Handling and Logging

Both `MessageProducer` and `MessageConsumer` include thorough error handling and logging to ensure smooth operation:
- Logs detailed information during message production and consumption.
- Provides real-time metrics for monitoring performance, such as frame rates and processing time.
- Handles synchronization and backlog errors gracefully to ensure reliable message processing.


## CV Modules

### Oveview

This section we will cover details about the CV modules pertaining to MCMOT, their configuration and how to run them individually and in a distributed environment.

All individual CV modules can be executed separately, but the streaming dependency follow this order:
`Capture → Detection → ReID → Tracker` → `Unification` → `Analytics`.

Tracker can be also connected directly with Capture to recieve captured frames directly for prediction and better accuracy.

The modules are independent of each other but connected using kafka topics. Flow of streaming frames and data happens through kakfa. At the same time if infrastructure is provisioned properly, multiple pipelines can run.

Each CV module is abstracted from kafka by two adapters - 1) MessageProducer and 2) MessageConsumer. These are part of the framework's Event module and placed in mcmot/framework/event. This python modules implements low level code for kafka and abstracts the complexity. These modules are part of mcmot/framework, which contains other common utilities that all the CV modules can use. The kafka configuration parameters like broker and topic related information are part of the PipelineConfiguration class as part of mcmot/framework/pipeline_configuration.py.

Each CV module has four components:
1) <module-name>_init.py
2) <module-name>_configuration.py
3) <module-name>_service.py
4) <module-name>_callback.py

The _init.py component receives the configuration json from command and creates a <Module>Configuration object which is defined in _configuration.py file. Then it creates an instance of <Module>Service class which is defined in _service.py passing the module configuration object and the pipeline configuration object. The service class creates the MessageProducer and MessageConsumer instances and starts listening to all the inbound topics. The MessageConsumer provides a callback which is programmed in the <Module>Callback class in _callback.py. The callback() method in <Module>Callback class is called from MessageConsumer when a message appears in the inbound kafka topic. This method provides the actual purpose and computation of the CV module. Optionally all modules can be configured for proper frame synchronization, which helps ensure that frames from multiple cameras or video feeds remain in sync.
 
Each module needs the broker configuration and the pipeline name along with its module configuration. Apart from that it takes the frame synchronization configuration, which is mentioned in a separate section.
All configuration can be passed as a json data as part of the python <module-name>_init.py command or the configuration can be kept in a json file and refer the path in the command.
All module ensures no data is lost or corruption occurs, even when interrupted (e.g., via keyboard signal or control command). It stops consumers and releases resources cleanly. All modules handle invalid messages or interruptions gracefully, ensuring proper cleanup and logging.

The logging utility is in mcmot/framework/utils and all modules generates logs in All module logs in mcmot/logs directory. The log configuration is located in mcmot/config/log. Any errors are logged for review without impacting the overall system.

---

### Capture Module

The **Capture Module** is designed to manage video frame acquisition from cameras, video files, or other streaming sources. It provides a reliable and customizable interface for video capture, ensuring smooth operation in real-world scenarios such as multi-camera setups, frame synchronization, and robust handling of errors or disruptions. By seamlessly integrating with message-driven systems (e.g., Kafka), the module serves as the entry point for downstream processing pipelines, such as analytics or monitoring systems.

---

#### Key Features

1. **Flexible Capture Sources**:
   - Supports capturing frames from multiple sources:
     - Physical cameras.
     - Stored video files.
     - Network streams.

2. **Customizable Capture Settings**:
   - Configurable options to define:
     - **Camera metadata**: Unique identifiers, location, and other contextual details.
     - **Output formats**: Video file formats (e.g., `AVI`, `MP4`).
     - **Compression and encoding**: Specify codec, compression type, and bitrate for efficient storage and transmission.

3. **Automatic Frame Synchronization**:
   - Ensures frames from multiple camera streams remain aligned, especially useful for downstream multi-camera tracking systems.

4. **Reliability and Error Handling**:
   - Handles sudden disruptions or disconnections gracefully:
     - Reconnects to the source as needed.
     - Resumes capture from the last successfully processed frame.

5. **Scalable Integration**:
   - Publishes captured frames (and metadata) to Kafka topics, enabling seamless integration across distributed systems.
   - Stateless design allows deployment of multiple instances for parallelized multi-camera operations.

6. **Offline Video Management**:
   - Supports captured video storage for offline processing.
   - Facilitates multi-camera setups for Regions of Interest (ROIs).

---

#### Configuration

Before running the module, users need to define the configuration parameters. These settings determine the behavior, format, and output of the capture process.

1. **Core Configuration Fields**:
   - **`module-config`**:
     - Specifies capture-related settings:
       - **`camera-id`**: A unique identifier for the camera.
       - **`location`**: The camera's physical location or region of interest.
       - **`format`**: The output format for captured video (e.g., `AVI`, `MP4`).
       - **`compression`**: Compression type (e.g., `H.265`).
       - **`bitrate`**: Bitrate for video encoding (e.g., `6Mbps`).
       - **`encoding`**: Encoding standard (e.g., `HEVC`).

   - **`frame-sync`**:
     - Optional settings for frame synchronization:
       - Enables temporal alignment of frames across multiple cameras.
       - Fields include the synchronization method, retention time, and the handling of initial delays.

2. **Dynamic Capture Configuration Attributes**:
   - **`camera_metadata`**: Stores camera-specific contextual data.
   - **`video_path`**: Path to the output/captured video location.
   - **`loop_count`**: Number of iterations for the capture operation, useful in testing scenarios.

---

#### Workflow

1. **Initialization**:
   - The module reads configurations (inline or from a JSON file) to initialize the `CaptureConfiguration` class.
   - Metadata such as `camera_id`, `location`, and `output format` is mapped to setup the capture process.

2. **Frame Capture**:
   - Loops over the video source (file or live camera feed), extracting frames and generating metadata for each.
   - Metadata is tagged with information like timestamps, frame numbers, and camera details.

3. **Synchronization and Publishing**:
   - Synchronizes frames (if enabled), aligning camera streams in multi-camera setups.
   - Sends frames and metadata to a Kafka topic for processing by downstream modules (e.g., analytics).

4. **Error Handling**:
   - Monitors the video source for disconnections or errors.
   - Automatically attempts reconnection and resumes the capture process.

---

#### How to Run

The module can be executed using the following command, specifying capture parameters inline for single-camera capture scenarios:

```bash
PYTHONPATH=. poetry run python capture/capture_init.py '{
  "pipeline": "test",
  "bootstrap-servers":["localhost:9092"],
  "module-config":{
    "camera-id": "4",
    "location": "terrace",
    "format": "avi",
    "compression": "H.265",
    "bitrate": "6Mbps",
    "encoding": "HEVC"
  },
  "frame-sync": {}
}'
```

- **Configuration File**: Instead of inline commands, a JSON configuration file can be used for convenience:
  ```bash
  PYTHONPATH=. poetry run python capture/capture_init.py config/capture-config.json
  ```

- **Multi-Camera Capture**:
  - For each camera stream, a separate process must be spawned with a unique **`camera-id`**.
  - Different angles or ROIs require independent capture processes.

---

#### Regions of Interest (ROIs)

Below is a list of predefined ROIs and their associated cameras and formats. Captured videos are stored in the `mcmot/capture/videos` directory for offline usage.

| ROI Name   | Cameras | Format |
|------------|---------|--------|
| basketball | 123     | avi    |
| terrace    | 1234    | avi    |
| store      | 12      | mp4    |
| belt       | 1234    | mp4    |
| road       | 123     | mp4    |
| zone       | 1       | mp4    |  
| corridor   | 12      | mp4    |  

---

#### Example Outputs

1. **Live Frame Output**:
   - Frames captured from the video source are tagged with metadata, such as:
     - Camera ID.
     - Timestamp.
     - Frame number.

2. **Offline Videos**:
   - Captured videos are stored locally in the configured path with specified format and compression settings for future processing.

3. **Published Data**:
   - Frames and relevant metadata are sent to a Kafka topic for real-time consumption by downstream services.

---

#### Summary

The **Capture Module** ensures seamless and scalable video frame acquisition, enabling robust systems for real-time data processing and offline storage. It provides flexibility for diverse video capture use cases, from single-camera setups to synchronized multi-camera workflows.

### Detection Module

The **Detection Module** represents the first stage in the object tracking pipeline. It consumes frames from an inbound Kafka topic, processes them using a YOLO model, and publishes detection results to an outbound Kafka topic. Additionally, it provides Kalman filter-based predictions to enhance robustness when object tracking is required between actual detection frames.

---

#### Overview

The Detection Module is a stateless, scalable service designed to perform object detection using a YOLO-based deep learning model. It supports distributed processing and can work in tandem with the downstream Tracker or ReID modules. Configured through JSON, it adapts to different pipelines, ensuring reliable object detection even in high-performance environments.

---

#### Key Features

##### 1. Detection Pipeline
- Processes video frames using the specified YOLO model.
- Detects objects of interest by filtering based on confidence thresholds and a defined set of target classes (e.g., `["person", "car"]`).

##### 2. Frame Synchronization
- Incorporates frame synchronization options to ensure temporally aligned and consistent frame processing in distributed environments. Capture module uses frame synchronization to maintain the FPS. It uses the skip_or_wait() function to do that.

##### 3. Predictive Enhancements
- Utilizes Kalman filters for object prediction to handle skipped frames or improve the robustness of object tracking when enabled.

##### 4. Kafka Integration
- **Inbound Kafka Topic**: Receives frames as input generated from upstream pipelines (e.g., Capture Module).
- **Outbound Kafka Topic**: Publishes detection results to downstream services (e.g., Tracker Module).

##### 5. Flexible Configuration
- Configurable via JSON to specify model files, classes of interest, and processing parameters.
- Optionally supports frame synchronization or predictive tracking for enhanced flexibility.

---

#### Key Components

##### **Configuration Parameters**

   - **`model`**: File path to the YOLO model weights to be used for detection (e.g., `"detection/model/yolov8s.pt"`).
   - **`classes`**: List of object classes to detect (e.g., `["person"]`).
   - **`confidence_score`**: Minimum confidence score for valid detections (default: `0.5`).
   - **`prediction`**: Boolean flag to enable predictions using Kalman filters; useful when frame synchronization is not enabled (default: `false`).
   - **`device-type`**: Specifies the computational device (`"cpu"` or `"cuda"`, default: `"cuda"` if available).

##### **Core Classes**
1. **`DetectionConfiguration`**:
   - Manages and validates detection-specific settings, including model configuration, target classes, and predictive behavior.

2. **`DetectionService`**:
   - Core component managing the detection pipeline, responsible for:
     - Consuming frames from Kafka topics.
     - Running object detection through the YOLO model.
     - Applying Kalman filters for predictions if enabled.
     - Publishing the results to downstream topics.

3. **`FrameSynchronizer`**:
   - Ensures temporal alignment of received frames in distributed systems, avoiding frame backlog issues.

---

#### Workflow

1. **Initialization**:
   - Loads JSON configuration containing pipeline and module settings.
   - Initializes the YOLO model, Kalman filter (if enabled), and Kafka consumers/producers.
   - Optionally sets up frame synchronization for distributed pipelines.

2. **Detection**:
   - Frames are consumed from the inbound Kafka topic.
   - Each frame undergoes object detection through the YOLO model.
   - Results are filtered by confidence score and target classes.

3. **Predictions (Optional)**:
   - If enabled, frames without detections undergo object prediction using Kalman filters.
   - This ensures continuous tracking and smoother predictions for skipped frames.

4. **Result Publishing**:
   - Detection results, including bounding boxes, class IDs, confidence scores, and frame metadata, are published to the outbound Kafka topic.

---

#### Key Functionalities

##### 1. YOLO-Based Object Detection
- Processes each frame to detect objects of interest using a specified YOLO model.
- Filters detections based on user-defined confidence threshold and classes.

##### 2. Kalman Filter-Based Prediction
- Applies Kalman filters to interpolate object positions and provide predictions in skipped frames when enabled.

##### 3. Frame Synchronization
- Aligns distributed processing pipelines by buffering or discarding out-of-sync frames.

##### 4. Scalable Execution
- The detection process is stateless and can run multiple parallel instances for scalability while leveraging Kafka's partitioning.

---

#### Use Cases


1. **Real-Time Object Detection**:
   - Detects objects such as people or vehicles in real-time for downstream processing modules (Tracker or ReID).

2. **Surveillance and Monitoring**:
   - Enables robust detection for surveillance systems where real-time object data is critical.

3. **Distributed Pipelines**:
   - Provides reliable and scalable detection services in multi-instance, Kafka-based distributed pipelines.

4. **Object Prediction**:
   - Enhances accuracy and continuity of tracking pipelines with predictive capabilities, especially for single-camera scenarios.

---

#### How to Run

To run the Detection Module as a standalone process, use the following command with inline JSON configuration:

```bash
PYTHONPATH=. poetry run python detection/detection_init.py '{
  "pipeline": "test",
  "bootstrap-servers": ["localhost:9092"],
  "module-config": {
    "model": "detection/model/yolov8n.pt",
    "classes": ["person"],
    "prediction": false
  },
  "frame-sync": {
    "ignore-initial-delay": false,
    "backlog-threshold": 3,
    "backlog-check-interval": 1,
    "type": "timestamp",
    "retention-time": 300
  }
}'
```

Alternatively, for better reusability, store the configuration in a JSON file and run the following command:

```bash
PYTHONPATH=. poetry run python detection/detection_init.py config/module/detection-config.json
```

---

#### Notes on Configuration

1. **Frame Synchronization and Prediction**:
   - If `frame-sync` is enabled, set the Kalman filter-based `prediction` to `false` for higher accuracy.
   - If `frame-sync` is not provided, enable `prediction` for smoother object tracking by predicting 50% of skipped frames.

2. **Partitioning for Scalability**:
   - Ensure the Kafka inbound topic (e.g., capture topic) has the same number of partitions as the number of detection instances for even distribution of workload.
   - For example, if four detection processes are deployed, the Kafka topic should have four partitions.

---

#### Default Outputs

The Detection Module publishes processed results to the outbound Kafka topic. Each message includes:
- Frame metadata: Frame number, timestamp.
- Detection results: Bounding boxes, class IDs, confidence scores.

The results are ready for downstream modules such as Tracker or ReID for further processing.


### ReID Module

The **ReID (Re-identification)** module performs person re-identification across frames in a video stream. By utilizing a pre-trained deep learning model, this module assigns unique IDs to detected objects (e.g., people) by extracting embeddings and matching them across successive frames. It is designed to integrate seamlessly into a distributed pipeline and supports a message-driven architecture for scalability.

The ReID module is essential for multi-camera multi-object tracking (MCMOT), but it is optional for single-camera setups. The Tracker Module can be directly linked to the Detection Module if re-identification is not required. Ideally, the ReID Module generates embeddings for each detected object and assigns IDs using cosine similarity, enabling consistent tracking IDs for objects appearing across multiple cameras.

This module benefits greatly from GPU acceleration for faster processing. However, it can also function on CPUs, albeit with reduced performance. Frame synchronization mechanisms can ensure minimal frame drops and consistent FPS.

---

#### Overview

The ReID Module integrates seamlessly into distributed pipelines by leveraging Kafka for message-driven communication. It processes detected objects in video frames, crops them, extracts embeddings, and assigns persistent IDs for robust tracking. The module is configurable via JSON, allowing flexibility in defining device types, model paths, and synchronization settings.

It plays a critical role in re-identifying objects across multiple video streams, enhancing the accuracy and consistency of object tracking pipelines.

---

#### Key Features

##### 1. Re-identification Pipeline
- Extracts embeddings of detected objects using a pre-trained deep learning model (e.g., OSNet).
- Matches embeddings between frames to assign consistent unique IDs to objects across the pipeline.

##### 2. Message-driven Design
- Uses Kafka topics for scalable ingestion and distribution of frame data and re-identification results.
- Dynamically configures inbound and outbound Kafka topics for seamless integration into processing pipelines.

##### 3. Embedding Matching
- Matches embeddings across frames using cosine similarity, ensuring consistent identity assignment, even across cameras.

##### 4. Flexible Model Support
- Processes embeddings with customizable pre-trained ReID models specified in configuration.
- Allows runtime configuration of computational devices (`cpu`, `cuda`, `mps`).

##### 5. Stateless Processing
- Performs stateless execution, making it possible to scale horizontally by deploying multiple ReID processes simultaneously.

##### 6. Frame Synchronization
- Minimizes FPS drops in distributed systems by leveraging frame synchronization mechanisms to align frame processing rates.

---

#### Key Components

The ReID Module is composed of configurable parameters and processing services that interact to ensure accurate and consistent re-identification of objects.

##### **Configuration Parameters**
1. **Pipeline Configuration**:
   - Configures Kafka pipeline topics for dynamic message exchange.
   - **Example**: `"pipeline": "test"`

2. **Module Configuration (`module-config`)**:
   - **`device-type`**: Specifies the device for computations (`"mps"`, `"cpu"`, `"cuda"`) (default: `"cuda"` if available, otherwise `"cpu"`).
   - **`model`**: Path to the pre-trained ReID model file (e.g., `"reid/model/osnet_x1_0.pth"`).

3. **Frame Synchronization**:
   - Includes options like delay handling (`ignore-initial-delay`), backlog thresholds, and retention times for efficient frame management.

##### **Core Classes**
1. **`ReidConfiguration`**:
   - Handles configuration validation and encapsulates settings related to the model and device preferences.

2. **`ReidService`**:
   - The core of the ReID Module, responsible for processing inbound detection frames, extracting embeddings, and assigning unique IDs.

3. **`EmbeddingDatabase`**:
   - Maintains an in-memory database of known embeddings and their corresponding IDs for efficient lookup and matching.

4. **`ReidCallback`**:
   - Processes individual frames, crops detected objects, extracts embeddings, computes cosine similarity, and assigns IDs.

#### Workflow

---

1. **Initialization**:
   - Loads and validates configurations, initializing the pipeline, frame sync parameters, and ReID model.
   - Creates an instance of `ReidService` to handle processing tasks.

2. **Detection Processing**:
   - Receives object detection messages (frames, bounding boxes) via an inbound Kafka topic.
   - Crops detected objects based on their bounding boxes and preprocesses them for embedding extraction.
   - Embeddings are extracted from the cropped objects using the configured pre-trained ReID model.

3. **ID Assignment**:
   - Newly extracted embeddings are matched against the in-memory database of previously seen embeddings using cosine similarity.
   - If no match is found, a new unique ID is assigned to the detection.

4. **Output**:
   - Results, including the frame number, timestamp, object metadata (bounding boxes, confidence scores, class, and assigned IDs), are sent to the outbound Kafka topic for downstream consumption.

#### Key Functionalities

---

##### 1. Embedding Extraction
- Extracts object-level embeddings from detection crops using deep learning models.
- Supports pre-trained models for high accuracy.

##### 2. Cosine Similarity Matching
- Compares embeddings across frames using cosine similarity, ensuring precise ID assignment.

##### 3. ReID Parallelization
- Allows deployment of multiple instances of the ReID Module for scalability while maintaining partition consistency in Kafka topics.

##### 4. Frame Synchronization
- Mitigates performance issues in distributed pipelines by enabling proper alignment of ingest and processing rates.

##### 5. Stateless Execution
- Operates in a stateless manner, enabling horizontal scaling without inter-process dependency.

#### Use Cases

---

1. **Multi-Camera Multi-Object Tracking (MCMOT)**:
   - Re-identifies objects (e.g., people, vehicles) across multiple surveillance cameras to assign consistent global IDs.

2. **Retail Analytics**:
   - Tracks and identifies individuals or objects across multiple customer interaction zones.

3. **Smart Traffic Systems**:
   - Identifies vehicles as they move through a multi-camera-monitored region for tracking and analytics.

4. **Public Safety and Surveillance**:
   - Identifies and tracks people in large, distributed areas for security and crowd management.

#### How to Run

---

To run the ReID Module as a standalone process, use the following command with inline configuration:

```bash
PYTHONPATH=. poetry run python reid/reid_init.py '{
  "pipeline": "test",
  "module-config": {
    "device-type": "mps",
    "model": "reid/model/osnet_x1_0.pth"
  },
  "frame-sync": {
    "ignore-initial-delay": false,
    "backlog-threshold": 5,
    "backlog-check-interval": 1,
    "type": "timestamp",
    "seek-to-end": false,
    "retention-time": 300
  }
}'
```

Alternatively, you can specify a configuration JSON file instead of inline configuration:

```bash
PYTHONPATH=. poetry run python reid/reid_init.py config/module/reid-config.json
```

#### Scalability

---

The ReID module can scale horizontally by running multiple instances on the same or different machines. Ensure that the partition count of the inbound detection topic matches the number of active ReID processes.

For example:
- If 4 ReID processes are deployed, the detection topic should have 4 partitions to distribute workload evenly.

#### Default Outputs

---

The processed results are sent to the outbound Kafka topic. Each message contains:
- Frame number.
- Timestamp.
- Object metadata (bounding boxes, confidence scores, class).
- Assigned unique IDs for consistent object identification.

### Tracker Module

The **Tracker Module** is responsible for object tracking across frames within a video stream, enabling the association of detections over time. Leveraging DeepSort and Kalman Filters, this module establishes consistent object IDs and handles state prediction, matching, and long-term track maintenance. 

This is the most complex module; it takes frames from either the detection or ReID module and creates tracker IDs for all detections. If frame synchronization is set in the detection or ReID module, frames may be skipped to maintain consistent FPS. For improved accuracy, undetected frames from the capture module must also be processed, applying predictions on the missing or skipped frames. Neglecting this step may reduce tracking performance and accuracy.

---

#### Overview

The Tracker Module is configured via a JSON file, enabling users to define critical thresholds, matching behaviors, and frame synchronization details. It integrates tightly with detection modules (e.g., ReID or object detection), processes raw video frames, and provides real-time tracking data to downstream modules through Kafka-based messaging.

---

#### Key Features

##### 1. Object Association
- Tracks objects across video frames using IoU-based matching and state prediction.
- Assigns persistent IDs to objects for consistent tracking over time.

##### 2. Integration with Detection Modules
- Seamlessly integrates with detections (e.g., from the ReID or detection module) as input sources for object tracking.

##### 3. Kalman Filter-Based Prediction
- Employs Kalman Filters to predict object states when frames are skipped, or detections are unavailable.

##### 4. Frame Synchronization
- Ensures temporal and spatial consistency of input frames, especially in distributed systems where camera feeds vary.

##### 5. Flexible Configuration
- Allows output customization, enabling users to focus on confirmed tracks or all detected objects.

##### 6. Efficient Frame Caching
- Implements in-memory caching to process historical frames, improving tracking reliability and continuity.

---

#### Key Components

The Tracker Module is composed of several configurable parameters and components aimed at providing robust tracking capabilities.

##### **Configuration Parameters**
- **`max-iou-distance`**: Maximum IoU distance when matching detections to tracks (default: `0.6`).
- **`max-age`**: Maximum number of frames a track can remain active without an update (default: `10`).
- **`nms-max-overlap`**: Maximum non-max suppression overlap for bounding boxes (default: `1.0`).
- **`gating-only-position`**: Indicates if object association uses position only (default: `true`).
- **`only-confirmed-tracks`**: Outputs confirmed tracks only (default: `false`).
- **`detection-score-threshold`**: Minimum confidence score for detections (default: `0.6`).
- **`match-detection`**: Enforces detection-to-track matching (default: `true`).
- **`ignore-capture`**: Ignores capture frames; impacts tracking accuracy when `true` (default: `false`).
- **`prediction-factor`**: Determines how much undetected capture data is considered during prediction (default: `0.5`).
- **`detection-module-name`**: Specifies which module supplies detections (default: `"reid"`).

##### **Core Classes**
1. **`TrackerConfiguration`**:
   - Manages and validates all tracker-specific settings.
   - Includes parameters like `max_iou_distance`, `max_age`, `match_detection`, and more.

2. **`TrackerService`**:
   - Orchestrates the tracking process through Kafka integration.
   - Manages message consumers for both detections and captures and performs the tracking pipeline.

3. **`TrackerDetectionCallback`**:
   - Contains the detection-to-track matching logic, as well as IoU calculations and Kalman Filter prediction.

4. **`TrackerCaptureCallback`**:
   - Processes raw camera frames and incorporates them into the tracking pipeline for missing frame prediction.

---

#### Workflow

1. **Initialization**:
   - Reads the JSON configuration to set up:
     - Tracker module parameters (e.g., `max-iou-distance`).
     - Frame synchronization rules.
     - Input data sources (e.g., Kafka topics for detections and captures).

2. **Processing**:
   - Captures raw camera frames and detection data.
   - Combines detection-based tracking with frame prediction from Kalman Filters for smoother results.
   - Handles late-arrival frames via caches or skipped detections for increased tracking accuracy.

3. **Track Updates**:
   - Matches new detections to existing tracks using IoU-based matching.
   - Predicts states when detections are unavailable and updates tracks based on their confidence levels.

4. **Output**:
   - Publishes tracked object data, including bounding boxes, object IDs, and confidence levels, to the outbound Kafka topic.

---

#### Key Functionalities

1. **DeepSort-Based Tracking**:
   - Combines IoU-based bounding box matching, non-max suppression, and Kalman Filter predictions to track objects.

2. **Frame Caching**:
   - Uses in-memory caching for historical frame retention, reducing the impact of missing detections.

3. **Robust State Predictions**:
   - Fills in gaps in frame data by predicting future states using Kalman Filters.

4. **Error Handling**:
   - Ensures tracking remains reliable despite skipped frames, synchronization issues, or temporary detection loss.

---

#### Use Cases

1. **Multi-Camera Object Tracking**:
   - Track individuals across multiple angles in real-time.

2. **Surveillance Footage Analysis**:
   - Analyze and monitor activity in crowded areas, assigning consistent IDs to individuals over time.

3. **Traffic Monitoring**:
   - Monitor vehicles traveling across intersections, matching objects even when not detected in consecutive frames.

4. **Retail and Customer Analytics**:
   - Identify customer patterns in stores across multiple cameras using consistent object tracking.

---

#### How to Run

To run the tracker module as a separate process, use the following command with a sample inline configuration:

```bash
PYTHONPATH=. poetry run python tracker/tracker_init.py '{
  "pipeline": "test",
  "module-config": {
    "max-iou-distance": 0.6,
    "max-age": 10,
    "nms-max-overlap": 1.0,
    "match-detection": true,
    "detection-score-threshold": 0.6,
    "gating-only-position": true,
    "ignore-capture": false,
    "prediction-factor": 0.5,
    "detection-module-name": "reid",
    "only-confirmed-tracks": false
  },
  "frame-sync": {
    "ignore-initial-delay": false,
    "backlog-threshold": 10,
    "backlog-check-interval": 1,
    "type": "timestamp",
    "retention-time": 300,
    "seek-to-end": false,
    "enable-sequencing": false
  }
}'
```

The inline configuration can also be replaced with a JSON file:

```bash
PYTHONPATH=. poetry run python tracker/tracker_init.py config/module/tracker-config.json
```
---

#### Scalability

A single tracker process can handle multiple camera inputs. To scale further, you can run separate Tracker Module instances for each camera. Ensure the Kafka inbound topic is partitioned correctly (e.g., if you run 4 tracker processes, the inbound topic must have 4 partitions).

---

#### Default Outputs

The output of the Tracker Module is written to the designated Kafka topic. The message contains bounding box coordinates, object IDs, and other relevant tracking details.

---

### Unification Module

The **Unification Module** is designed to unify multiple data sources (such as video frames or messages) into a structured and harmonized output. Leveraging advanced synchronization and processing capabilities, it integrates seamlessly with Kafka and other components of the pipeline. The module is configured to process messages, combine related data, and generate unified outputs, such as annotated media files or structured metadata.

---

#### Overview

The Unification Module is composed of key components that work together to support the unification pipeline. These include configuration handlers (`UnificationConfiguration`), processing services (`UnificationService`), callback implementation (`UnificationCallback`), and Kafka integration for message production and consumption.
The Unification Module is a critical component for real-time streaming data systems, enabling seamless integration, powerful synchronization, and efficient unification of diverse data sources. Its configurable nature and advanced features make it highly adaptable to various real-time applications across industries such as media processing, IoT, and analytics.

---

#### Key Features

##### 1. UnificationService
The `UnificationService` is the core manager for coordinating all unification operations. It handles Kafka's inbound and outbound messaging, synchronizes incoming data, and ensures proper configuration for tasks such as message filtering and frame processing.

- Manages the lifecycle of message consumers and producers.
- Integrates with the pipeline configuration for Kafka topics.
- Synchronizes and sequences inbound data using the `FrameSyncService`.
- Processes unified outputs while ensuring robust error handling.

##### 2. UnificationConfiguration
This class encapsulates all configurable parameters needed for the unification process. By defining output paths, API settings, and customizable prompts, the configuration allows the module to be flexible and adaptable.

- **Output Location**: Specifies the directory for storing unified media and metadata.
- **API Key**: Supports integration with external APIs, if applicable.
- **Prompt**: Allows customization of operation instructions (e.g., for image analysis or frame annotation).

##### 3. UnificationCallback
The `UnificationCallback` acts as the processing engine for consuming and processing inbound messages. It is responsible for grouping related data, annotating frames, generating metadata, and producing unified outputs.

- **Message Handling**: Processes incoming messages, groups frame data by camera or time, and stores metadata.
- **Frame Unification**: Combines frames into structured outputs, such as grid-based images or videos.
- **Output Generation**: Generates unified outputs (e.g., combined videos, logs, or JSON metadata) and saves them to disk.
- **Message Production**: Sends processed results back to a Kafka topic for downstream consumers.

##### 4. Kafka Integration
The module leverages Kafka for message consumption and production, supporting real-time streaming pipelines:
- **Inbound Kafka Topics**: Consumes messages to process and unify frame data.
- **Outbound Kafka Topics**: Produces unified outputs (e.g., metadata, videos) for distribution across the pipeline.

---

#### Key Functionalities

1. **Data Synchronization**:
   - Aligns frames or messages from multiple sources using timestamps, frame numbers, or custom synchronization logic.
   - Ensures proper sequencing of data for downstream operations.

2. **Combined Output Generation**:
   - Groups related data and combines it into unified outputs.
   - Outputs may include combined images, videos, structured metadata (e.g., JSON files), or logs.

3. **Custom Processing**:
   - Allows users to define callbacks for custom business logic in processing frames, metadata extraction, and output generation.
   - Supports annotation of frames with bounding boxes, metadata, and additional visual overlays.

4. **Error Handling**:
   - Monitors and resolves issues during the unification pipeline, including invalid frames, message deserialization, and more.
   - Logs all errors for better debugging and traceability.

5. **Performance Optimization**:
   - Handles high-throughput scenarios efficiently using threading, backlogs, and lock-based synchronization mechanisms.
   - Ensures minimal latency in producing unified outputs.

---

#### Use Cases

1. **Unified Video Frame Processing**:
   - Unify frames received from multiple cameras into annotated, time-synchronized outputs.

2. **Real-Time Media Pipelines**:
   - Process streaming data from sensors or cameras and produce unified metadata for analytics.

3. **Industrial Monitoring Systems**:
   - Consolidate data from multiple IoT sources into cohesive insights for predictive maintenance and real-time monitoring.

4. **Metadata Enrichment**:
   - Generate annotated media outputs with unified metadata for documentation or further analysis.

---

#### How to Run

Unification cannot scale and has to always run as a single process. 

```bash
PYTHONPATH=. poetry run python unification/unification_init.py '{
  "pipeline": "test",
  "module-config": {
    "output": "./output"
  },
  "frame-sync": {
    "ignore-initial-delay": false,
    "backlog-threshold": 5,
    "backlog-check-interval": 1,
    "type": "timestamp",
    "retention-time": 1000,
    "unify": true,
    "enable-sequencing": false
  }
}
'
```

The inline configuration can be replaced by keeping the json configuration in a separate json file and refer the file in the command.
Note that here in frame-sync, the unify is set to true.

```bash
PYTHONPATH=. poetry run python unification/unification_init.py config/module/unification-config.json
```
The output of the unification is stored in the mcmot/output directory by default, if not otherwise specified in the module-config's `output` location. It creates jpg images of all the frames from all the cameras for a timestamp as a group and store the images in a group directory. It also creates a combined frame from all the cameras in the group directory. If the unification process is stopped or on hold for 60 seconds it will close the combined video containing all the synchronized combined frames. 

---

### Analytics Module

The **Analytics Module** is designed to enrich camera-based outputs with analytical insights powered by language models. It processes metadata and visual data from cameras and generates detailed descriptions, logs, and Excel reports. The module provides an interface for real-time analytics, allowing users to perform deeper analysis of connected camera feeds and their outputs.

---

#### Key Features

1. **AI-Powered Insights**:
   - Leverages language models (e.g., **OpenAI GPT** or **ChatOllama**) to generate textual insights based on incoming camera frame data and metadata.
   - Produces descriptive observations for grouped camera data.

2. **Multimodal Processing**:
   - Processes video frames, metadata, and combined images for structured analysis.
   - Supports integration of both textual and visual inputs for generating responses.

3. **Customizable Prompt and Configurations**:
   - The behavior of the language model interaction is easily configurable through:
     - Custom prompts for generating descriptions.
     - API key support for dynamic language model selection.
   - Flexible options for logging frequency and output paths.

4. **Data Aggregation and Reporting**:
   - Generates detailed log entries for grouped camera frame metadata and AI observations.
   - Saves analytics results to Excel workbooks, enabling structured reporting and tracking.

5. **Stream-Based Analytics**:
   - Integrates seamlessly with Kafka topics for consuming data streams.
   - Supports synchronization for managing grouped frames from multiple camera sources.

6. **Scalable and Stateless**:
   - Stateless design allows multiple instances of the module to process data in parallel for real-time, large-scale pipelines.

---

#### Key Components

##### **Analytics Configuration**

- **Logging and Reporting**:
  - **`log_wait_time`**: Configures the interval in seconds between log entries.
  - **Output Path**:
    - **`output`**: Directory for saving logs (`.log`) and Excel files (`.xlsx`).

- **Language Model Interaction**:
  - **`api_key`**: Toggles between language models:
    - If provided: Uses OpenAI GPT.
    - If omitted: Defaults to ChatOllama.
  - **`prompt`**: Customizable prompt sent to the language model to contextualize the analysis.

---

##### **How It Works**

The Analytics Module runs a real-time pipeline using a messaging framework (e.g., Kafka), processes messages with the analytics callback, and produces written and visual outputs.

1. **Pipeline Configuration**:
   - Connects to Kafka topics to ingest grouped camera frames and metadata.
   - Synchronizes grouped frames across multiple cameras using `FrameSyncConfiguration`.

2. **Analytics Processing**:
   - Frames and metadata are passed to the **`AnalyticsCallback`**.
   - The callback interacts with the language model:
     - Generates textual descriptions or insights using the configured prompt.
     - Maintains historical context for enabling iterative analysis.

3. **Data Logging and Reporting**:
   - Logs observations into structured text files with timestamps.
   - Saves structured entries into Excel workbooks for easy analysis and future reference.

4. **Real-Time Execution**:
   - Processes frames within a defined time interval to ensure responsiveness.
   - Handling of grouped frames enables insights into scenes captured by multiple cameras collectively.

---

#### Workflow

1. **Initialization**:
   - Reads configurations to set up the **AnalyticsService**.
   - Configures logging, analytics behavior (e.g., prompt definition, intervals), and output handling.

2. **Frame Group Handling**:
   - Ingests grouped camera frames and associated metadata.
   - Combines frame data for cross-camera analysis and invokes language models to infer and describe key observations.

3. **Language Model Invocation**:
   - Processes structured prompts and visual data via AI:
     - Sends a combined image with extracted metadata to a supported language model.
     - Uses the model's response to provide detailed insights for grouped frames.

4. **Logging and Reporting**:
   - Saves insights and metadata logs into `.log` text files and `.xlsx` spreadsheet reports.
   - Logs are timestamped for traceability and structured for Excel-based data analysis.

5. **Scalable Processing**:
   - Designed to operate in a stateless mode for large-scale message-driven architectures.
   - Multiple instances can run in parallel for higher throughput in distributed environments.

---

#### Key Classes and Methods

1. **`AnalyticsConfiguration`**
   - Stores and validates the configuration for language model interaction and underlying analytics reporting.
   - Key attributes:
     - **`output`**: Directory for saving logs and reports.
     - **`log_wait_time`**: Interval between log entries.
     - **`prompt`**: Prompt definition for AI insights.

2. **`AnalyticsService`**
   - The core service that manages the pipeline:
     - Initializes Kafka consumers.
     - Frames the required callback and analytics configurations.
   - Primary methods:
     - **`__init__`**: Configures pipeline, frame synchronization, and the callback.
     - **`process`**: Handles the main loop for message consumption and processing.

3. **`AnalyticsCallback`**
   - Provides the main processing logic:
     - Combines images and metadata for grouped camera frames.
     - Invokes the language model to generate insights.
     - Saves observational results in structured log and Excel reports.
   - Includes:
     - **`callback`**: Processes each grouped frame event.
     - **`invoke_llm`**: Interacts with the language model for generating responses.

---

#### How to Run

The analytics module uses either OpenAI or Ollama. If OpenAI api-key is provided then it will use OpenAI otherwise it will try to look for local Ollama server. To run the Analytics Module as a standalone process, use the following command:

```bash
PYTHONPATH=. poetry run python analytics/analytics_init.py '{
  "pipeline": "test",
  "bootstrap-servers": ["localhost:9092"],
  "module-config": {
    "output": "/path/to/output",
    "api-key": "<your_openai_api_key>",
    "log-wait-time": 60,
    "prompt": "Describe the image."
  },
  "frame-sync": {
    "ignore-initial-delay": false,
    "backlog-threshold": 10,
    "backlog-check-interval": 5,
    "enable-sequencing": true,
    "type": "timestamp",
    "retention-time": 300
  }
}'
```

Alternatively, you can use a configuration file:

```bash
PYTHONPATH=. poetry run python analytics/analytics_init.py config/analytics-config.json
```

---

#### Example Outputs

1. **Log File (`.log`)**:
   - Contains structured textual entries for each camera group and associated analysis.
   - Example entry:
     ```
     Time: 2023-11-05 14:30:15
     Camera-Frame Number-Frame Timestamp: 1-100-1699200615, 2-200-1699200616
     Observation: The scene includes two cameras. Camera 1 detects a crowded area. Camera 2 identifies an empty corridor.
     --------------------------------------------------
     ```

2. **Excel Report (`.xlsx`)**:
   - Organizes the same data in tabular format, with columns for timestamps, grouped frames, and observations.

---

#### Scalability
Only one analytics module must be running as its processes the combined frames from all the cameras.

### Observability Module

The **Observability Module** is responsible for visualizing processing pipeline information by overlaying critical metadata such as timestamps, frame numbers, frames-per-second (FPS), camera IDs, and bounding boxes on video frames. It enables real-time monitoring and debugging for object detection and tracking pipelines. The module consumes processed frames from a Kafka topic and outputs annotated frames with the specified visualization settings.
This module is not part of the CV module pipeline and works horizontally for all modules, but works exactly like the CV modules. Its composition is also similar to other CV modules. Its solves the cross-cutting concern of realtime monitoring of each CV module of the pipeline.
---

#### Key Features

1. **Real-Time Observability**:
   - Displays metadata (e.g., timestamps, frame numbers, FPS, and camera IDs) overlaid on processed frames.
   - Annotates frames with bounding boxes and labels for detected objects.

2. **Customizable Visualization**:
   - Configurable text and bounding box attributes, including color and thickness.
   - Flexible options to enable or disable metadata visualization.

3. **Kafka Integration**:
   - **Inbound Kafka Topic**: Consumes frames with detection and metadata from upstream processing pipelines.
   - Processes the metadata or detection results for visualization tasks.

4. **Frame Synchronization**:
   - Integrates optional synchronization mechanisms to ensure alignment of frames in distributed systems.

5. **Stateless and Scalable**:
   - Leverages a stateless design to support scaling by deploying multiple instances for large-scale pipelines.

---

#### Key Components

##### **Observability Configuration**
The module is highly configurable, and visualization settings can be adjusted using the following options:

- **Metadata Display**:
  - **`show_timestamp`**: Displays the timestamp for each frame.
  - **`show_frame_number`**: Displays the frame number (processed count and total).
  - **`show_fps`**: Displays calculated FPS and target FPS.
  - **`show_camera_id`**: Displays the camera ID for the current frame.

- **Annotation and Style**:
  - **`text_color`**: Defines the text color, with options such as `red`, `blue`, `green`, or **RGB** tuples.
  - **`text_thickness`**: Specifies the thickness of the text annotations.
  - **`box_color`**: Configures the bounding box color for detections.
  - **`box_thickness`**: Sets the thickness of bounding box outlines.

- **Detection Header Parameter**:
  - **`detection_header_parameter`**: Specifies the metadata field (e.g., `id` or similar) to display for each detection.

---

##### **How It Works**

The Observability Module is implemented as a service (`ObservabilityService`) that processes frames, annotates metadata, and displays the resulting frames in real time using OpenCV.

1. **Pipeline and Frame Synchronization**:
   - The module connects to a Kafka inbound topic specified by the `PipelineConfiguration`.
   - Optional frame synchronization ensures frame alignment according to the `FrameSyncConfiguration`.

2. **Annotations and Overlays**:
   - Frames are processed using the **`ObservabilityCallback`**, which overlays metadata and annotations onto the frames.
   - The module uses OpenCV for visualizing the processed frames in real time.

3. **Display Processing**:
   - Metadata for detections, such as bounding boxes, IDs, and additional information, is dynamically rendered onto the frame.
   - Customizable features, including font size, annotation colors, and bounding box styles, are applied based on developer preferences.

4. **Stateless Execution**:
   - The service is stateless and designed to be horizontally scalable. Multiple instances can be run to balance load in distributed pipelines.

---

#### Workflow

1. **Initialization**:
   - Reads configuration from a JSON file or command-line arguments.
   - Initializes the `ObservabilityCallback` for handling annotations and frame overlays.
   - Configures a Kafka consumer to ingest processed frame data from the inbound topic.

2. **Frame Processing**:
   - For every message received:
     - Decodes the frame (Base64-encoded video frame).
     - Annotates the frame with bounding boxes, metadata, and overlay text.
     - Computes and shows FPS, timestamps, frame counts, and other visual elements on the frame.

3. **Display**:
   - Renders the annotated frame using the OpenCV `imshow` utility in a pop-up window titled according to the module name and camera ID.

4. **Graceful Shutdown**:
   - The process listens for interrupts (`Ctrl+C`) to perform cleanup, closing any OpenCV windows and Kafka consumer connections.

---

#### Key Classes and Methods

1. **`ObservabilityConfiguration`**
   - Captures and validates configuration settings such as colors, font size, visibility flags, and detection metadata parameters.

2. **`ObservabilityService`**
   - Implements the main processing loop:
     - Ingests messages via Kafka.
     - Executes `ObservabilityCallback` for annotation and frame metadata processing.

3. **`ObservabilityCallback`**
   - Handles visualization logic, including annotation of bounding boxes, text overlays, and other metadata rendering.
   - Includes methods for:
     - **`annotate_frame`**: Draws bounding boxes and detection labels on frames.
     - **`initialize_frame_dimensions`**: Calculates frame dimensions for consistent scaling and positioning of annotations.
     - **`callback`**: Processes metadata and applies all annotations for each received frame.

---

#### How to Run

To run the Observability Module as a standalone process, use the following command with sample inline configuration:

```bash
PYTHONPATH=. poetry run python observability/observability_init.py '{
  "pipeline": "test",
  "bootstrap-servers": ["localhost:9092"],
  "module-config": {
    "module": "capture",
    "detection_header_parameter": "id",
    "text-color": "blue",
    "text-thickness": 2,
    "box-color": "green",
    "box-thickness": 2,
    "show-frame_number": true,
    "show-timestamp": true,
    "show-fps": true,
    "show-camera-id": true
  },
  "frame-sync": {
    "ignore-initial-delay": false,
    "backlog-threshold": 5,
    "backlog-check-interval": 1,
    "type": "timestamp",
    "retention-time": 300
  }
}'
```

Alternatively, you can specify a JSON configuration file like this:

```bash
PYTHONPATH=. poetry run python observability/observability_init.py config/observability/observability-config.json
```

---

#### Example Outputs

Observability opens up python windows to show the frames in continuous motion for each module and for each camera. The observability instance read from the pertaining module's outbound topic. The observability instance to module mapping is done in the module-config's `module` attribute. 
Each frame is displayed with annotations based on the configured settings, such as:
- **Bounding boxes** for detected objects.
- **FPS** (calculated and target FPS).
- **Metadata**: Timestamp, camera IDs, and frame numbers.

Annotated frames are rendered in OpenCV pop-up windows, aiding in real-time monitoring and debugging.

---

#### Scalability

- The module can run multiple instances in parallel. if a module has to be observed in the runtime, then we have to make sure its corresponding observability instance is running. Multiple windows will open up if one module is processing frames from multiple camera captures.

## License

This project is under Apache License 2.0

## Author

Conceptualized and developed by **Anirban Chakraborty**.  
For queries or feedback, email: **anirban.c1@tcs.com**.