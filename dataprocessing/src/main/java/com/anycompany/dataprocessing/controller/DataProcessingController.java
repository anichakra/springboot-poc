package com.anycompany.dataprocessing.controller;

import java.util.List;

import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import com.anycompany.dataprocessing.model.SomeFeed;
import com.anycompany.dataprocessing.repository.DataProcessingRepository;

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

	@GetMapping("/dataProcessing")
	public String ping() {
		return "Success";
	}

	@RequestMapping(value = "/someFeedDataProcessing", method = RequestMethod.POST, consumes = MediaType.APPLICATION_JSON_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
	@ApiOperation(value = "Read somefeed data and send it as JSON response")
	@ResponseBody
	@ApiResponses(value = { @ApiResponse(code = 200, message = "Success Response"),
			@ApiResponse(code = 500, message = "Error while processing some feed Data") })
	public String processHrFeedData(@RequestBody List<SomeFeed> dataList) {
		long startTime = System.currentTimeMillis();
		repo.save(dataList);
		long stopTime = System.currentTimeMillis();
		long elapsedTime = stopTime - startTime;
		LOG.info(elapsedTime);
		return "success";

	}

}
