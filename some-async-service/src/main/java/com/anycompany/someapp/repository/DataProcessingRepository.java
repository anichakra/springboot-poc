package com.anycompany.someapp.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Component;

import com.anycompany.someapp.model.SomeFeed;

@Component
public interface DataProcessingRepository extends JpaRepository<SomeFeed, Integer>{
} 
