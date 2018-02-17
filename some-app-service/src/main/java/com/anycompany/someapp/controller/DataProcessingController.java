package com.anycompany.someapp.controller;

import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.anycompany.someapp.service.SomeFeedService;
import com.netflix.hystrix.contrib.javanica.annotation.HystrixCommand;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiResponse;
import io.swagger.annotations.ApiResponses;

@RestController
@Api(value = "Data-Processing-App", description = "This is Data Processing controller")
public class DataProcessingController {

	@Autowired
	@Qualifier("someFeedServiceImpl")
	private SomeFeedService service;

	@PostMapping(value = "/uploadFile")
	@ApiOperation(value = "Upload single file using Spring Controller")
	@ResponseBody
	@ApiResponses(value = { @ApiResponse(code = 200, message = "Success Response"),
			@ApiResponse(code = 500, message = "File not uploaded") })
	@HystrixCommand(fallbackMethod = "uploadFallback")
	public Map<String, String> uploadFileHandler(@RequestParam("file") MultipartFile file,
			@RequestParam("serviceType") String serviceType, HttpServletRequest request, HttpServletResponse response)
			throws IOException {
		return service.uploadFileHandler(file, serviceType);
	}

	@PostMapping(value = "/processRawSomeFeedData")
	@ApiOperation(value = "Read Some Feed raw data and send it as JSON response")
	@ResponseBody
	@ApiResponses(value = { @ApiResponse(code = 200, message = "Success Response"),
			@ApiResponse(code = 500, message = "Error while processing somefeed raw data") })
	public String processRawSomeFeedData(@RequestBody List<String> rawData) throws IOException {
		return service.processRawSomeFeedData(rawData);
	}

	@PostMapping(value = "/processSomefeedJsonData")
	@ApiOperation(value = "Read Some Feed json data and send it as Model response")
	@ResponseBody
	@ApiResponses(value = { @ApiResponse(code = 200, message = "Success Response"),
			@ApiResponse(code = 500, message = "Error while processing somefeed json data") })
	public String processSomefeedJsonData(@RequestBody String jsonData) throws IOException {
		return service.processSomefeedJsonData(jsonData);
	}

	public Map<String, String> uploadFallback(@RequestParam("file") MultipartFile file,
			@RequestParam("serviceType") String serviceType, HttpServletRequest request, HttpServletResponse response) {
		return Collections.singletonMap("Response", "Fallback Response");
	}

}
