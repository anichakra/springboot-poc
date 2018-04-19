package me.anichakra.springboot.poc.some.data.service;

import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/users")
public class SomeDataController {

    @RequestMapping(value = "/user/{id}", method = RequestMethod.GET)
    public String user(@PathVariable(value = "id") Long id){
        return "user-"+id;
    }

}
