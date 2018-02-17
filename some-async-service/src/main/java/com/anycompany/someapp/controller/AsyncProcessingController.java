package com.anycompany.someapp.controller;

import java.io.IOException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import com.anycompany.someapp.service.DataProcessingService;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiResponse;
import io.swagger.annotations.ApiResponses;

@RestController
@Api(value = "Async-Processing-App", description = "This is Async Processing controller")
public class AsyncProcessingController {

	@Autowired 
	@Qualifier("dataProcessingServiceImpl")
	private DataProcessingService service;
	

	@PostMapping(value = "/processFileAsync")
	@ApiOperation(value = "This resource will process file data asynchronously")
	@ResponseBody
	@ApiResponses(value = { @ApiResponse(code = 200, message = "Success Response"),
			@ApiResponse(code = 500, message = "Error while processing file") })
	public String processRawSomeFeedData(@RequestBody String fileName) throws IOException {
		return service.processFile(fileName);
	}
	

}
