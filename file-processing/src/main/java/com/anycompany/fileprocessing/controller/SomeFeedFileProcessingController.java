package com.anycompany.fileprocessing.controller;

import java.io.IOException;
import java.util.List;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.apache.log4j.Logger;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import com.anycompany.fileprocessing.model.SomeFeedModel;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiResponse;
import io.swagger.annotations.ApiResponses;

@RestController
@Api(value = "SomeFeed-Fileprocessing-App", description = "This is somefeed file processing controller")
@RefreshScope
public class SomeFeedFileProcessingController {

	private static final Logger LOG = Logger.getLogger(SomeFeedFileProcessingController.class);

	@PostMapping(value = "/processRawSomeFeedData")
	@ApiOperation(value = "Read Some Feed raw data and send it as JSON response")
	@ResponseBody
	@ApiResponses(value = { @ApiResponse(code = 200, message = "Success Response"),
			@ApiResponse(code = 500, message = "Error while processing somefeed raw data") })
	public String processRawSomeFeedData(@RequestBody List<String> rawData) throws IOException {
		return processInputDataAsJson(rawData);
	}

	@PostMapping(value = "/processSomefeedJsonData")
	@ApiOperation(value = "Read Some Feed json data and send it as Model response")
	@ResponseBody
	@ApiResponses(value = { @ApiResponse(code = 200, message = "Success Response"),
			@ApiResponse(code = 500, message = "Error while processing somefeed json data") })
	public List<SomeFeedModel> processSomefeedJsonData(@RequestBody String jsonData) throws IOException {
		LOG.trace(jsonData);
		ObjectMapper objectMapper = new ObjectMapper();
		return objectMapper.readValue(jsonData, new TypeReference<List<SomeFeedModel>>() {
		});
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
	
}
