package me.anichakra.poc.auth.service;

import java.util.Collection;

import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.GrantedAuthority;

import me.anichakra.poc.common.security.AdditionalTokenDetails;
import me.anichakra.poc.common.security.UserDetails;

/**
 * This class used to build the response for UsernamePasswordAuthenticationToken 
 * @author MTakate
 *
 */
public class RoleBasedAuthToken extends UsernamePasswordAuthenticationToken {

	private static final long serialVersionUID = 1L;

	private UserDetails customuserDetails;
	
	private String roles;
	
	private AdditionalTokenDetails additional;
	
	public RoleBasedAuthToken(Object principal, Object credentials,
			Collection<? extends GrantedAuthority> authorities) {
		super(principal, credentials, authorities);

	}

	public UserDetails getCustomuserDetails() {
		return customuserDetails;
	}

	public void setCustomuserDetails(UserDetails customuserDetails) {
		this.customuserDetails = customuserDetails;
	}

	public AdditionalTokenDetails getAdditional() {
		return additional;
	}

	public void setAdditional(AdditionalTokenDetails additional) {
		this.additional = additional;
	}

	public String getRoles() {
		return roles;
	}

	public void setRoles(String roles) {
		this.roles = roles;
	}


}
