package me.anichakra.poc.user.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
/**
 * Upload service specific internal resources
 *
 */
@Configuration
@ConfigurationProperties(prefix = "internal.resources")
public class UserInternalResourceConfig {

	private String ioservice;
	
	private String saveAuditRecord;

	public String getIoservice() {
		return ioservice;
	}

	public void setIoservice(String ioservice) {
		this.ioservice = ioservice;
	}

	public String getSaveAuditRecord() {
		return saveAuditRecord;
	}

	public void setSaveAuditRecord(String saveAuditRecord) {
		this.saveAuditRecord = saveAuditRecord;
	}
	
}
