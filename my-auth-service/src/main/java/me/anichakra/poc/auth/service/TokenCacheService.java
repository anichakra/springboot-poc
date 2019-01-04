package me.anichakra.poc.auth.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.security.oauth2.common.OAuth2AccessToken;
import org.springframework.stereotype.Service;

import me.anichakra.poc.common.security.CacheService;
/**
 * TokenCacheService used for cache the JSON Web Token
 * @author MTakate
 *
 */
@Service
public class TokenCacheService {
	private static final String TOKEN_CACHE = "tokenCache";
	
	@Autowired
	private CacheService cacheService;
	/**
	 * Insert the values in provided cache with username as key and token as value
	 * @param username
	 * @param token
	 */
	public void put(String username, OAuth2AccessToken token) {
		cacheService.put(TOKEN_CACHE, username, token);
	}

	/**
	 * Retrive the token by providing cache name and key 
	 * @param username
	 * @return
	 */
	public OAuth2AccessToken get(String username) {
		return (OAuth2AccessToken) cacheService.get(TOKEN_CACHE, username);
	}

	/**
	 * Remove the value value from cache by providing cache name and key
	 * @param username
	 */
	public void remove(String username) {
		cacheService.remove(TOKEN_CACHE, username);
	}
}
