package com.anycompany.someapp.service;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import org.springframework.web.multipart.MultipartFile;

public interface SomeFeedService {

	public Map<String, String> uploadFileHandler(MultipartFile file,String serviceType) throws IOException;

	public String processRawSomeFeedData(List<String> rawData) throws IOException;

	public String processSomefeedJsonData(String jsonData) throws IOException;
}
