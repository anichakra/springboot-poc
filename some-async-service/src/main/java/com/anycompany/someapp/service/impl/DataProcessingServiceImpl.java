package com.anycompany.someapp.service.impl;

import java.io.IOException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.anycompany.someapp.service.DataProcessingService;

@Component
public class DataProcessingServiceImpl implements DataProcessingService {


	@Autowired
	private AsyncDataProcessServiceImpl asyncService;

	@Override
	public String processFile(String fileName) throws IOException {
		asyncService.startProcessing(fileName);
		return "success";
	}
}
