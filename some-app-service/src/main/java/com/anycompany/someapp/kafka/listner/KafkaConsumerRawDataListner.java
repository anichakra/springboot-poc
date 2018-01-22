package com.anycompany.someapp.kafka.listner;

import java.io.IOException;
import java.util.List;

import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

import com.anycompany.someapp.controller.DataProcessingController;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

@Component
public class KafkaConsumerRawDataListner {

	private static final Logger LOG = Logger.getLogger(KafkaConsumerRawDataListner.class);

	@Autowired
	DataProcessingController controller;

	@KafkaListener(topics = "chunk", group = "group-someFeed")
	public void kafkaListner(String chunkString) {
		ObjectMapper objectMapper = new ObjectMapper();

		try {
			List<String> chunk = objectMapper.readValue(chunkString, new TypeReference<List<String>>() {
			});
			controller.processRawSomeFeedData(chunk);
			System.out.println("Data processed size" + chunk.size());
		} catch (IOException e) {
			LOG.error(e);
		}

	}

}
