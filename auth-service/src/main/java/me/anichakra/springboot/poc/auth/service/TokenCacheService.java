package me.anichakra.springboot.poc.auth.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.cache.CacheManager;
import org.springframework.security.oauth2.common.OAuth2AccessToken;
import org.springframework.stereotype.Service;

@Service
@ConfigurationProperties(prefix="hz")
public class TokenCacheService {

	private Integer port;
    private String group;
    private String secret;
    private List<>
	
	@Autowired
	private CacheManager cacheManager;
	public OAuth2AccessToken getAccessToken() {
		cacheManager.
	}

	public void remove(String name) {
		// TODO Auto-generated method stub
		
	}

}
