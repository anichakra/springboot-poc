package me.anichakra.poc.springboot.pilot.vehicle.service;

import java.util.List;
import java.util.Optional;

import me.anichakra.poc.springboot.pilot.vehicle.domain.Category;
import me.anichakra.poc.springboot.pilot.vehicle.domain.Vehicle;

/**
 * This is the vehicle service
 * @author Anirban
 *
 */
public interface VehicleService {

	Vehicle saveVehicle(Vehicle vehicle);
	
	Optional<Vehicle> getVehicle(Long id);
	
	void deleteVehicle(Long id);
	
	List<Vehicle> searchVehicle(String manufacturer);

    Vehicle getPreference(Category category);
}
