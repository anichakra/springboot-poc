package com.anycompany.dataprocessing.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Component;

import com.anycompany.dataprocessing.model.SomeFeed;

@Component
public interface DataProcessingRepository extends JpaRepository<SomeFeed, Integer>{
} 
