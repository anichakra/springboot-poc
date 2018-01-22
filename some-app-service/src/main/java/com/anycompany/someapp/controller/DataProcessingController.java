package com.anycompany.someapp.controller;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.anycompany.someapp.model.SomeFeed;
import com.anycompany.someapp.model.SomeFeedModel;
import com.anycompany.someapp.repository.DataProcessingRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.netflix.hystrix.contrib.javanica.annotation.HystrixCommand;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiResponse;
import io.swagger.annotations.ApiResponses;

@RestController
@Api(value = "Data-Processing-App", description = "This is Data Processing controller")
public class DataProcessingController {

	private static final Logger LOG = Logger.getLogger(DataProcessingController.class);

	@Autowired
	DataProcessingRepository repo;

	@Value("${upload.path}")
	private String uploadRootPath;

	@Value("${upload.folder}")
	private String uploadFolder;

	@Autowired
	private KafkaTemplate<String, String> kafkaTemplate;

	@PostMapping(value = "/uploadFile")
	@ApiOperation(value = "Upload single file using Spring Controller")
	@ResponseBody
	@ApiResponses(value = { @ApiResponse(code = 200, message = "Success Response"),
			@ApiResponse(code = 500, message = "File not uploaded") })
	@HystrixCommand(fallbackMethod = "uploadFallback")
	public Map<String, String> uploadFileHandler(@RequestParam("file") MultipartFile file, HttpServletRequest request,
			HttpServletResponse response) throws IOException {
		if (!file.isEmpty()) {
			byte[] bytes = file.getBytes();
			String name = file.getOriginalFilename();
			// Creating the directory to store file
			String rootPath = uploadRootPath;
			File dir = new File(new File(rootPath), uploadFolder);
			if (!dir.exists())
				dir.mkdirs();
			// Create the file on server
			File serverFile = new File(new File(dir.getAbsolutePath()), name);
			outputFileWriter(bytes, serverFile);
			LOG.info("Server File Location= " + serverFile.getAbsolutePath());
			kafkaTemplate.send("filePath", serverFile.getAbsolutePath());
		}
		return Collections.singletonMap("Response", "Success");
	}

	private void outputFileWriter(byte[] bytes, File serverFile) throws FileNotFoundException, IOException {
		try (BufferedOutputStream stream = new BufferedOutputStream(new FileOutputStream(serverFile))) {
			stream.write(bytes);
		}
	}

	@PostMapping(value = "/processRawSomeFeedData")
	@ApiOperation(value = "Read Some Feed raw data and send it as JSON response")
	@ResponseBody
	@ApiResponses(value = { @ApiResponse(code = 200, message = "Success Response"),
			@ApiResponse(code = 500, message = "Error while processing somefeed raw data") })
	public String processRawSomeFeedData(@RequestBody List<String> rawData) throws IOException {
		String jsonInput = processInputDataAsJson(rawData);
		processSomefeedJsonData(jsonInput);
		return "success";
	}

	@PostMapping(value = "/processSomefeedJsonData")
	@ApiOperation(value = "Read Some Feed json data and send it as Model response")
	@ResponseBody
	@ApiResponses(value = { @ApiResponse(code = 200, message = "Success Response"),
			@ApiResponse(code = 500, message = "Error while processing somefeed json data") })
	public String processSomefeedJsonData(@RequestBody String jsonData) throws IOException {
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

	public Map<String, String> uploadFallback(@RequestParam("file") MultipartFile file, HttpServletRequest request,
			HttpServletResponse response) {
		return Collections.singletonMap("Response", "Fallback Response");
	}
}
