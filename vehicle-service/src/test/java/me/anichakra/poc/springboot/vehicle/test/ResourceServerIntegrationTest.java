package me.anichakra.poc.springboot.vehicle.test;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;
import org.springframework.test.context.junit4.SpringRunner;

import me.anichakra.poc.springboot.vehicle.DomainServiceApplication;

@RunWith(SpringRunner.class)
@SpringBootTest(classes = DomainServiceApplication.class, webEnvironment = WebEnvironment.RANDOM_PORT)
public class ResourceServerIntegrationTest {

    @Test
    public void whenLoadApplication_thenSuccess() {

    }
}
