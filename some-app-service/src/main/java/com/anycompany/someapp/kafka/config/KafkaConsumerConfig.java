package com.anycompany.someapp.kafka.config;

import java.util.HashMap;
import java.util.Map;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaConsumerFactory;



@Configuration
@EnableKafka
public class KafkaConsumerConfig {

	@Bean
	@ConditionalOnMissingBean(ConsumerFactory.class)
	public ConsumerFactory<Object, Object> consumerFactory() {
		Map<String, Object> consumerConfigProperties = new HashMap<>();
		consumerConfigProperties.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
		consumerConfigProperties.put(ConsumerConfig.GROUP_ID_CONFIG, "group-someFeed");
		consumerConfigProperties.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
		consumerConfigProperties.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
		return new DefaultKafkaConsumerFactory<>(consumerConfigProperties);
	}

	@Bean
	@ConditionalOnMissingBean(name = "kafkaListenerContainerFactory")
	public ConcurrentKafkaListenerContainerFactory<Object, Object> kafkaListnerContainerFacory() {
		ConcurrentKafkaListenerContainerFactory<Object, Object> kafkaFactory = new ConcurrentKafkaListenerContainerFactory<>();
		kafkaFactory.setConsumerFactory(consumerFactory());
		return kafkaFactory;
	}
}
