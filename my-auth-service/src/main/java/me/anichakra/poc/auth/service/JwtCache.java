package me.anichakra.poc.auth.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.oauth2.common.OAuth2AccessToken;
import org.springframework.security.oauth2.provider.OAuth2Authentication;
import org.springframework.security.oauth2.provider.token.store.JwtAccessTokenConverter;
import org.springframework.security.oauth2.provider.token.store.JwtTokenStore;
import org.springframework.stereotype.Component;
/**
 * JwtCache used for cache the JSON Web Token
 * @author MTakate
 *
 */
@Component
public class JwtCache extends JwtTokenStore{

	@Autowired
	private TokenCacheService tokenCacheService;
	
	public JwtCache(JwtAccessTokenConverter jwtTokenEnhancer) {
		super(jwtTokenEnhancer);
	}
	/**
	 * Cache the JSON Web token
	 */
	@Override
	public void storeAccessToken(OAuth2AccessToken token, OAuth2Authentication authentication) {
		tokenCacheService.put(authentication.getUserAuthentication().getName().toLowerCase(), token);
	}
}
