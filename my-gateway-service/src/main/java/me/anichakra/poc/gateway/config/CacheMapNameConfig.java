package me.anichakra.poc.gateway.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
/**
 * This class is useful for access the cache names from yml
 * @author MTakate
 *
 */
@Configuration
@ConfigurationProperties(prefix="cache.map.name")
public class CacheMapNameConfig {

	private String accessToken;
	private String refreshToken;
	private String usernameRefreshToken;
	private String usernameAccessToken;
	
	public String getAccessToken() {
		return accessToken;
	}
	public void setAccessToken(String accessToken) {
		this.accessToken = accessToken;
	}
	public String getRefreshToken() {
		return refreshToken;
	}
	public void setRefreshToken(String refreshToken) {
		this.refreshToken = refreshToken;
	}
	public String getUsernameRefreshToken() {
		return usernameRefreshToken;
	}
	public void setUsernameRefreshToken(String usernameRefreshToken) {
		this.usernameRefreshToken = usernameRefreshToken;
	}
	public String getUsernameAccessToken() {
		return usernameAccessToken;
	}
	public void setUsernameAccessToken(String usernameAccessToken) {
		this.usernameAccessToken = usernameAccessToken;
	}
	
}
