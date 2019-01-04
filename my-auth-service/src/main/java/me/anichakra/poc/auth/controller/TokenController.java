package me.anichakra.poc.auth.controller;

import javax.annotation.Resource;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.oauth2.common.OAuth2AccessToken;
import org.springframework.security.oauth2.common.OAuth2RefreshToken;
import org.springframework.security.oauth2.provider.OAuth2Authentication;
import org.springframework.security.oauth2.provider.token.ConsumerTokenServices;
import org.springframework.security.oauth2.provider.token.TokenStore;
import org.springframework.security.oauth2.provider.token.store.JdbcTokenStore;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import me.anichakra.poc.auth.service.TokenCacheService;
/**
 * Token Controller provides the rest end points to revoke token from user  
 * @author MTakate
 *
 */
@Controller
public class TokenController {

	@Autowired
	TokenCacheService cacheService;

	@Resource(name = "tokenServices")
	ConsumerTokenServices tokenServices;

	@Resource(name = "tokenStore")
	TokenStore tokenStore;
	/**
	 * By passing tokenId as parameter it will revoke the access token for respective user
	 * @param tokenId
	 */
	@RequestMapping(method = RequestMethod.POST, value = "/oauth/token/revokeById/{tokenId}")
	@ResponseBody
	public void revokeToken(@PathVariable String tokenId) {
		tokenServices.revokeToken(tokenId);
	}
	/**
	 * Revoked the access and refresh token by using the username
	 * @param username
	 * @return
	 */
	@PreAuthorize("#oauth2.hasScope('ENTERPRISEAPI_ADMIN')")
	@RequestMapping(method = RequestMethod.POST, value = "/tokens/revokeTokenByUsername/{username}")
	@ResponseBody
	public String revokeTokenByUsername(@PathVariable String username) {
		OAuth2AccessToken accessToken = (OAuth2AccessToken) cacheService.get(username);
		
		if (null != accessToken) {
			OAuth2RefreshToken refreshToken = accessToken.getRefreshToken();
			if (null != refreshToken) {
				revokeRefreshToken(refreshToken.getValue());
			}
			revokeToken(String.valueOf(accessToken));
			return "Token revoked successfully...";
		}
		return null;
	}
	/**
	 * Revoked the refresh token by using refresh tokenId.
	 * @param tokenId
	 * @return
	 */
	@RequestMapping(method = RequestMethod.POST, value = "/tokens/revokeRefreshToken/{tokenId:.*}")
	@ResponseBody
	public String revokeRefreshToken(@PathVariable String tokenId) {
		if (tokenStore instanceof JdbcTokenStore) {
			((JdbcTokenStore) tokenStore).removeRefreshToken(tokenId);
		} else {
			OAuth2Authentication auth2Authentication = tokenStore.readAuthentication(tokenId);
			cacheService.remove(auth2Authentication.getName());
		}
		return tokenId;
	}
}