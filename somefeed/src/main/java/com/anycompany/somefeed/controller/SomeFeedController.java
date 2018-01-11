package com.anycompany.somefeed.controller;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import com.anycompany.somefeed.model.SomeFeedModel;
import com.netflix.hystrix.contrib.javanica.annotation.HystrixCommand;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiResponse;
import io.swagger.annotations.ApiResponses;

@RestController
@Api(value = "Some-Feed-App", description = "This is Some Feed inbound controller")
@RefreshScope
public class SomeFeedController {

	private static final Logger LOG = Logger.getLogger(SomeFeedController.class);

	@Value("${upload.path}")
	private String uploadRootPath;

	@Value("${upload.folder}")
	private String uploadFolder;

	@Autowired
	RestTemplate template;

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
			HttpEntity<String> fileRequest = new HttpEntity<>(serverFile.getAbsolutePath());
			ResponseEntity<String> fileResponse = template.postForEntity("http://kafka-producer/createFileEvent",
					fileRequest, String.class);
			System.out.println(fileResponse.getBody());
		}
		return Collections.singletonMap("Response", "Success");
	}

	private void outputFileWriter(byte[] bytes, File serverFile) throws FileNotFoundException, IOException {
		try (BufferedOutputStream stream = new BufferedOutputStream(new FileOutputStream(serverFile))) {
			stream.write(bytes);
		}
	}

	public Map<String, String> uploadFallback(@RequestParam("file") MultipartFile file, HttpServletRequest request,
			HttpServletResponse response) {
		return Collections.singletonMap("Response", "Fallback Response");
	}

	@PostMapping(value = "/processSomeFeedData")
	@ApiOperation(value = "Processing some feed input data")
	@ResponseBody
	@ApiResponses(value = { @ApiResponse(code = 200, message = "Success Response"),
			@ApiResponse(code = 500, message = "Error while processing some feed inbound data") })
	public String processSomeFeedData(@RequestBody List<String> rawData) throws IOException {
		HttpEntity<List<String>> rawDataRequest = new HttpEntity<>(rawData);
		ResponseEntity<String> jsonResponse = template.postForEntity("http://file-processing/processRawSomeFeedData",
				rawDataRequest, String.class);
		HttpEntity<String> jsonDataRequest = new HttpEntity<>(jsonResponse.getBody());
		ResponseEntity<SomeFeedModel[]> modelResponse = template.postForEntity(
				"http://file-processing/processSomefeedJsonData", jsonDataRequest, SomeFeedModel[].class);
		List<SomeFeedModel> modelList = Arrays.asList(modelResponse.getBody());
		// TODO : Spring data rest call here with input as modelList

		HttpEntity<List<SomeFeedModel>> dataRequest = new HttpEntity<>(modelList);
		ResponseEntity<String> response = template.postForEntity(
				"http://dataprocessing/someFeedDataProcessing", dataRequest, String.class);

		return "success";
	}

}
