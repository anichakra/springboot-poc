package com.anycompany.someapp.service.impl;

import java.io.IOException;
import java.io.InputStream;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import com.anycompany.someapp.model.S3UploadFileModel;
import com.anycompany.someapp.model.SomeFeed;
import com.anycompany.someapp.model.SomeFeedModel;
import com.anycompany.someapp.repository.DataProcessingRepository;
import com.anycompany.someapp.s3.S3Actions;
import com.anycompany.someapp.service.SomeFeedService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

@Component
public class SomeFeedKafkaServiceImpl implements SomeFeedService {

	private static final Logger LOG = Logger.getLogger(SomeFeedKafkaServiceImpl.class);

	@Autowired
	DataProcessingRepository repo;

	@Autowired
	private S3Actions action;

	@Autowired
	private KafkaTemplate<String, String> kafkaTemplate;

	public Map<String, String> uploadFileHandler(MultipartFile file,String serviceType) throws IOException {
		if (!file.isEmpty()) {
			InputStream stream = file.getInputStream();
			String name = file.getOriginalFilename();
			S3UploadFileModel uploadRequest = new S3UploadFileModel(name, stream, null);
			String result = action.postFileToS3(uploadRequest);
			LOG.info("File has been uploaded in S3 with result as :" + result);

			// pushing filename to kafka
			kafkaTemplate.send("fileName", name);
		}
		return Collections.singletonMap("Response", "Success");
	}

	public String processRawSomeFeedData(List<String> rawData) throws IOException {
		String jsonInput = processInputDataAsJson(rawData);
		processSomefeedJsonData(jsonInput);
		return "success";
	}

	public String processSomefeedJsonData(String jsonData) throws IOException {
		LOG.trace(jsonData);
		ObjectMapper objectMapper = new ObjectMapper();
		List<SomeFeed> modelInput = objectMapper.readValue(jsonData, new TypeReference<List<SomeFeed>>() {
		});
		processData(modelInput);
		return "success";
	}

	private String processInputDataAsJson(List<String> input) {
		ObjectMapper objectMapper = new ObjectMapper();
		// Set pretty printing of json
		objectMapper.enable(SerializationFeature.INDENT_OUTPUT);
		try {
			return objectMapper.writeValueAsString(input.stream().map(mapToItem).collect(Collectors.toList()));
		} catch (JsonProcessingException e) {
			return "error";
		}
	}

	private Function<String, SomeFeedModel> mapToItem = (line) -> {
		String[] p = line.split(",");// a CSV has comma separated lines
		SomeFeedModel output = new SomeFeedModel(p[0], p[1], p[2], p[3], p[4]);
		LOG.trace(output);
		return output;
	};

	public String processData(List<SomeFeed> dataList) {
		long startTime = System.currentTimeMillis();
		repo.save(dataList);
		long stopTime = System.currentTimeMillis();
		long elapsedTime = stopTime - startTime;
		LOG.info(elapsedTime);
		return "success";

	}
}
