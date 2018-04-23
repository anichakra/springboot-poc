package me.anichakra.poc.springboot.vehicle;

import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurerAdapter;

@Configuration
@EnableWebMvc
@ComponentScan({ "org.baeldung.web.controller" })
public class ResourceServerWebConfig extends WebMvcConfigurerAdapter {
    //
}
