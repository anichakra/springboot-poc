package com.anycompany.someapp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.circuitbreaker.EnableCircuitBreaker;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.client.loadbalancer.LoadBalanced;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.cloud.netflix.eureka.EnableEurekaClient;
import org.springframework.cloud.sleuth.sampler.AlwaysSampler;
import org.springframework.cloud.sleuth.zipkin2.ZipkinProperties;
import org.springframework.cloud.sleuth.zipkin2.ZipkinRestTemplateCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

import zipkin2.reporter.Sender;

@EnableCircuitBreaker
@SpringBootApplication
@EnableEurekaClient
@EnableDiscoveryClient
@RefreshScope
@ComponentScan("com.anycompany")
public class SomeApplication {

	public static void main(String[] args) {
		SpringApplication.run(SomeApplication.class, args);
	}
	
	@Configuration
	class config {

		@LoadBalanced
		@Bean
		public RestTemplate restTemplate() {
			return new RestTemplate();
		}
	}
	
	@Bean
	public AlwaysSampler defaultSample() {
		return new AlwaysSampler();  
	}

	@Bean
	public Sender restTemplateSender(ZipkinProperties zipkin,
			ZipkinRestTemplateCustomizer zipkinRestTemplateCustomizer) {
		RestTemplate restTemplate = new RestTemplate();
		zipkinRestTemplateCustomizer.customize(restTemplate);
		return new CustomRestTemplateSender(restTemplate, zipkin.getBaseUrl(), zipkin.getEncoder());
	}
}
