package me.anichakra.poc.springboot.vehicle.web.security;

import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurerAdapter;

@Configuration
@EnableWebMvc
@ComponentScan({ "me.anichakra.poc.springboot.vehicle" })
public class ResourceServerWebConfig extends WebMvcConfigurerAdapter {
    //
}