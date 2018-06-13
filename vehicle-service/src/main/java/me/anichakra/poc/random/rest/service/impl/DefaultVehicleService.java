package me.anichakra.poc.random.rest.service.impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import me.anichakra.poc.random.rest.domain.Vehicle;
import me.anichakra.poc.random.rest.repo.VehicleRepository;
import me.anichakra.poc.random.rest.service.VehicleService;

@Service("default")
public class DefaultVehicleService implements VehicleService {
	
	@Autowired
	private VehicleRepository vehicleRepository;

	@Override
	public void saveVehicle(Vehicle vehicle) {
		vehicleRepository.saveAndFlush(vehicle);
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
