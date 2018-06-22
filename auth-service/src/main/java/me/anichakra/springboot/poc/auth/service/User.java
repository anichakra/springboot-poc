package me.anichakra.springboot.poc.auth.service;

import java.util.List;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter @Setter @NoArgsConstructor
public class User {

   private String id;
   private String firstName;
   private String lastName;
   private String email;
   private List<String> roles;
   
}
