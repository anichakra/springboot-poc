package me.anichakra.poc.springboot.vehicle.service.impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import me.anichakra.poc.springboot.vehicle.domain.Vehicle;
import me.anichakra.poc.springboot.vehicle.repo.VehicleRepository;
import me.anichakra.poc.springboot.vehicle.service.VehicleService;

@Service("default")
public class DefaultVehicleService implements VehicleService {
	
	@Autowired
	private VehicleRepository vehicleRepository;

	@Override
	public Vehicle saveVehicle(Vehicle vehicle) {
		return vehicleRepository.saveAndFlush(vehicle);
	}

	@Override
	public Vehicle getVehicle(Long id) {
		return vehicleRepository.findOne(id);
	}

	@Override
	public void deleteVehicle(Long id) {
	   vehicleRepository.delete(id);
	}

	@Override
	public List<Vehicle> searchVehicle(String manufacturer) {
		return vehicleRepository.findByManufacturer(manufacturer);
	}

}
