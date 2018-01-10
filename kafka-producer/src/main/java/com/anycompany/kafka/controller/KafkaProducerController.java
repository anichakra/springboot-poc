package com.anycompany.kafka.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import com.fasterxml.jackson.core.JsonProcessingException;

@RestController
public class KafkaProducerController {

	@Autowired
	private KafkaTemplate<String, String> kafkaTemplate;
	
	@PostMapping(value="/createFileEvent")
	public @ResponseBody String sendMessage(@RequestBody String filePath) throws JsonProcessingException {
			kafkaTemplate.send("filePath",filePath);	
		return "Message successfuly sent";
	}
	
}
