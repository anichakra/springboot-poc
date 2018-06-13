package me.anichakra.poc.random.rest.service;

import java.util.List;

import me.anichakra.poc.random.rest.domain.Vehicle;

/**
 * This is the vehicle service
 * @author Anirban
 *
 */
public interface VehicleService {

	void saveVehicle(Vehicle vehicle);
	
	Vehicle getVehicle(Long id);
	
	void deleteVehicle(Long id);
	
	List<Vehicle> searchVehicle(String manufacturer);
}
