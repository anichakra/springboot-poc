package com.anycompany.someapp.kafka.config;

import java.util.HashMap;
import java.util.Map;

import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringSerializer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.core.DefaultKafkaProducerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.core.ProducerFactory;


@Configuration
public class KafkaProducerConfig {

	@Value("kafka-host")
	private String kafkaHost;
	
	@Bean
	public ProducerFactory<String, String> producerFactory() {
		Map<String, Object> producerConfigProperties = new HashMap<>();
		producerConfigProperties.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, kafkaHost);
		producerConfigProperties.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
		producerConfigProperties.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
		return new DefaultKafkaProducerFactory<>(producerConfigProperties);
	}
	
	@Bean
	public KafkaTemplate<String, String> kafkaTemplate() {
		return new KafkaTemplate<>(producerFactory());
	}
	
}
