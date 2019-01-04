package me.anichakra.poc.auth.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
/**
 * Oauth security end points configuration. 
 * @author MTakate
 *
 */
@ConfigurationProperties(prefix="oauth.security.endpoints")
public class OauthSecurityEndpointConfig {
	
	private String revokeById;
	private String login;
	private String tokens;
	
	/**
	 * Revoke by id rest end point of Oauth security framework. 
	 * @return
	 */
	public String getRevokeById() {
		return revokeById;
	}
	public void setRevokeById(String revokeById) {
		this.revokeById = revokeById;
	}
	/**
	 * Login rest end point of Oauth security framework. 
	 * @return
	 */
	public String getLogin() {
		return login;
	}
	public void setLogin(String login) {
		this.login = login;
	}
	/**
	 * Tokens rest end point of Oauth security framework. 
	 * @return
	 */
	public String getTokens() {
		return tokens;
	}
	public void setTokens(String tokens) {
		this.tokens = tokens;
	}
	
}
