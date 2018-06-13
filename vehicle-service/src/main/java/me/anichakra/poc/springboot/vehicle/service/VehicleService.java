package me.anichakra.poc.springboot.vehicle.service;

import java.util.List;

import me.anichakra.poc.springboot.vehicle.domain.Vehicle;

/**
 * This is the vehicle service
 * @author Anirban
 *
 */
public interface VehicleService {

	Vehicle saveVehicle(Vehicle vehicle);
	
	Vehicle getVehicle(Long id);
	
	void deleteVehicle(Long id);
	
	List<Vehicle> searchVehicle(String manufacturer);
}
