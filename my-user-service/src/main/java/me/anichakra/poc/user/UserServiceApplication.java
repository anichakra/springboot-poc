package me.anichakra.poc.user;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

import me.anichakra.poc.user.config.Microservice;
@Microservice(scanBasePackages= {"me.anichakra"})
@EnableJpaRepositories("me.anichakra.poc.user.repository")
@EntityScan(basePackages = {"me.anichakra.poc.user.entity"} )
public class UserServiceApplication { 

	public static void main(String[] args) {
		SpringApplication.run(UserServiceApplication.class, args);
	}
	
}