package me.anichakra.poc.springboot.vehicle.web;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import me.anichakra.poc.springboot.vehicle.domain.Vehicle;
import me.anichakra.poc.springboot.vehicle.service.VehicleService;

@RestController
@RequestMapping("/vehicle")
public class VehicleController {

	@Autowired
	@Qualifier("default")
	private VehicleService vehicleService;
  
	@PreAuthorize("#oauth2.hasScope('bar') and #oauth2.hasScope('read')")
	@GetMapping("/{id}")
	@ResponseBody
	public Vehicle getVehicle(@PathVariable("id") Long id) {
		return vehicleService.getVehicle(id);
	}

	@PreAuthorize("#oauth2.hasScope('bar') and #oauth2.hasScope('write') and hasRole('ROLE_ADMIN')")
	@PostMapping
	@ResponseStatus(HttpStatus.CREATED)
	@ResponseBody
	public Vehicle saveVehicle(@RequestBody Vehicle vehicle) {
		return vehicleService.saveVehicle(vehicle);
	}

	@DeleteMapping
	public HttpStatus deleteVehicle(@RequestBody Vehicle vehicle) {
		vehicleService.deleteVehicle(vehicle.getId());
		return HttpStatus.OK;
	}

	@PostMapping("/search")
	public List<Vehicle> searchVehicle(@RequestParam("manufacturer") String manufacturer) {
		return vehicleService.searchVehicle(manufacturer);
	}

}
