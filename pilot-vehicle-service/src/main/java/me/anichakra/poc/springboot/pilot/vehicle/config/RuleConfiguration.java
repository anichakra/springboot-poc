package me.anichakra.poc.springboot.pilot.vehicle.config;

import javax.validation.constraints.NotNull;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.validation.annotation.Validated;

import me.anichakra.poc.springboot.pilot.framework.rule.RuleService;
import me.anichakra.poc.springboot.pilot.framework.rule.impl.OpenlTabletRuleService;
import me.anichakra.poc.springboot.pilot.vehicle.rule.VehicleRuleTemplate;

@Configuration
@ConfigurationProperties(prefix = "rule")
@Validated
public class RuleConfiguration {

    @NotNull
    String templatePath;

    public String getTemplatePath() {
        return templatePath;
    }

    public void setTemplatePath(String templatePath) {
        this.templatePath = templatePath;
    }

    @Bean(value = "vehicle")
    public RuleService<VehicleRuleTemplate> getVehicleRuleTemplate() {
        RuleService<VehicleRuleTemplate> vehicleRuleService = new OpenlTabletRuleService<VehicleRuleTemplate>();
        vehicleRuleService.loadRuleTemplate(templatePath, VehicleRuleTemplate.class);
        return vehicleRuleService;
    }

}
