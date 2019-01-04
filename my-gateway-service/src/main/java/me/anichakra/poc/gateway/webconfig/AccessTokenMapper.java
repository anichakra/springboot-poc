package me.anichakra.poc.gateway.webconfig;

import me.anichakra.poc.common.security.AdditionalTokenDetails;
import me.anichakra.poc.common.security.UserDetails;
/**
 * AccessTokenMapper is used to map the JWT response for the additional changes.
 * @author MTakate
 *
 */
public class AccessTokenMapper {

	private String access_token;
	private String token_type;
	private String refresh_token;
	private String expires_in;
	private String scope;
	private String jti;
	private UserDetails userDetails;
	private AdditionalTokenDetails additionalDetails;

	public String getAccess_token() {
		return access_token;
	}

	public void setAccess_token(String access_token) {
		this.access_token = access_token;
	}

	public String getToken_type() {
		return token_type;
	}

	public void setToken_type(String token_type) {
		this.token_type = token_type;
	}

	public String getRefresh_token() {
		return refresh_token;
	}

	public void setRefresh_token(String refresh_token) {
		this.refresh_token = refresh_token;
	}

	public String getExpires_in() {
		return expires_in;
	}

	public void setExpires_in(String expires_in) {
		this.expires_in = expires_in;
	}

	public String getScope() {
		return scope;
	}

	public void setScope(String scope) {
		this.scope = scope;
	}

	public String getJti() {
		return jti;
	}

	public void setJti(String jti) {
		this.jti = jti;
	}

	public UserDetails getUserDetails() {
		return userDetails;
	}

	public void setUserDetails(UserDetails userDetails) {
		this.userDetails = userDetails;
	}

	public AdditionalTokenDetails getAdditionalDetails() {
		return additionalDetails;
	}

	public void setAdditionalDetails(AdditionalTokenDetails additionalDetails) {
		this.additionalDetails = additionalDetails;
	}

}
