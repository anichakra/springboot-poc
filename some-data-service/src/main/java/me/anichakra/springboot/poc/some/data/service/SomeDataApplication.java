package me.anichakra.springboot.poc.some.data.service;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.eureka.EnableEurekaClient;

@SpringBootApplication
@EnableEurekaClient
public class SomeDataApplication 
{
    public static void main( String[] args )
    {
    	//System.setProperty("javax.net.ssl.trustStore", "C:/Users/218606/Desktop/jksfinal/eurekaFinal.jks");
    	//System.setProperty("javax.net.ssl.trustStorePassword", "eurekaFinal");
    	SpringApplication.run(SomeDataApplication.class, args);

    }
}


