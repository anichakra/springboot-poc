package me.anichakra.poc.springboot.pilot.vehicle.service.impl;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

import me.anichakra.poc.springboot.pilot.framework.rule.RuleService;
import me.anichakra.poc.springboot.pilot.vehicle.domain.Category;
import me.anichakra.poc.springboot.pilot.vehicle.domain.Vehicle;
import me.anichakra.poc.springboot.pilot.vehicle.repo.VehicleRepository;
import me.anichakra.poc.springboot.pilot.vehicle.rule.VehicleRuleTemplate;
import me.anichakra.poc.springboot.pilot.vehicle.service.VehicleService;

@Service("default")
public class DefaultVehicleService implements VehicleService {
    
    @Autowired
    @Qualifier("vehicle")
    private RuleService<VehicleRuleTemplate> ruleService;
    
    private VehicleRuleTemplate getRuleTemplate() {
        VehicleRuleTemplate vehicleRuleTemplate = ruleService.getRuleTemplate();
        return vehicleRuleTemplate;
    }
	@Autowired
	private VehicleRepository vehicleRepository;

	@Override
	public Vehicle saveVehicle(Vehicle vehicle) {
		return vehicleRepository.saveAndFlush(vehicle);
	}

	@Override
	public Optional<Vehicle> getVehicle(Long id) {
		return vehicleRepository.findById(id);
	}

	@Override
	public void deleteVehicle(Long id) {
	   vehicleRepository.deleteById(id);
	}

	@Override
	public List<Vehicle> searchVehicle(String manufacturer) {
		return vehicleRepository.findByManufacturer(manufacturer);
	}

    @Override
    public Vehicle getPreference(Category category) {
        return getRuleTemplate().getPreference(category, new Vehicle());
    }

}
