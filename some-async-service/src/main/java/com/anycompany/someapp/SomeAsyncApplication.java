package com.anycompany.someapp;

import org.springframework.beans.factory.annotation.Value;
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
import org.springframework.core.task.TaskExecutor;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.web.client.RestTemplate;

import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;

import zipkin2.reporter.Sender;

@EnableCircuitBreaker
@SpringBootApplication
@EnableEurekaClient
@EnableDiscoveryClient
@RefreshScope
@EnableAsync
@ComponentScan("com.anycompany")
public class SomeAsyncApplication {

	public static void main(String[] args) {
		SpringApplication.run(SomeAsyncApplication.class, args);
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

	@Value("${amazon.accessKey}")
	private String accessKey;

	@Value("${amazon.secretKey}")
	private String secretKey;

	@Bean
	public AmazonS3 amazonS3Client() {
		AWSCredentials credentials = new BasicAWSCredentials(accessKey, secretKey);
		AmazonS3 s3Client = AmazonS3ClientBuilder.standard()
				.withCredentials(new AWSStaticCredentialsProvider(credentials)).withRegion("us-east-1").build();
		return s3Client;
	}

	@Bean("asyncExecutor")
	public TaskExecutor taskExecuter() {
		ThreadPoolTaskExecutor task = new ThreadPoolTaskExecutor();
		task.setCorePoolSize(10);
		task.setMaxPoolSize(10);
		task.setQueueCapacity(5);
		task.afterPropertiesSet();
		return task;
	}
	
}
