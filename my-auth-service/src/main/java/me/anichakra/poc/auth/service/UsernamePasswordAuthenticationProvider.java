package me.anichakra.poc.auth.service;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import me.anichakra.poc.auth.domain.ClientDetailsEntity;
import me.anichakra.poc.auth.repository.eauth.EauthRestClient;
import me.anichakra.poc.common.EauthResponse;
import me.anichakra.poc.common.Roles;
import me.anichakra.poc.common.security.AdditionalTokenDetails;
import me.anichakra.poc.common.security.ClientDetails;
import me.anichakra.poc.common.security.UserDetails;

/**
 * UsernamePasswordAuthenticationProvider is the customized authentication
 * provider for our application
 * 
 * @author MTakate
 *
 */
@Component
public class UsernamePasswordAuthenticationProvider implements AuthenticationProvider {

	@Autowired
	EauthRestClient forgeRockAccess;

	@Autowired
	private ClientDetailService clientDetailsService;

	@Override
	public Authentication authenticate(Authentication authentication) {

		String name = authentication.getName();
		// Authenticating the user from forgerock
		EauthResponse forgerockToken = forgeRockAccess.getForgerockToken(authentication);

		if (StringUtils.isEmpty(forgerockToken.getAccess_token())) {
			RoleBasedAuthToken tokenResponse = new RoleBasedAuthToken(null, null, null);
			tokenResponse.setAuthenticated(false);
			return tokenResponse;
		}

		// Fetch permissions and basic user details from forge rock for authenticated
		// user
		Roles roles = forgeRockAccess.getPermissions(forgerockToken.getAccess_token());
		// Fetch the Client Details from the security database for authenticated user
		List<ClientDetailsEntity> clientDetailsEntity = getClientDetails(name);

		List<ClientDetails> clientDetails = clientDetailsEntity.stream().map(entityToModel)
				.collect(Collectors.toList());
		// create the UserDetails object with basic user details and client details

		UserDetails userDetails = new UserDetails();
		AdditionalTokenDetails tokenDetails = new AdditionalTokenDetails();
		if (null != roles) {
			userDetails.setEmailId(roles.getEmail());
			userDetails.setFirstName(roles.getFirstName());
			userDetails.setLastName(roles.getLastName());
			userDetails.setLogin(roles.getUid());
			userDetails.setUserType(roles.getUserType());
			userDetails.setPermissions(getPermissionsList(roles));
			userDetails.setClientDetails(clientDetails);

			tokenDetails.setTokenTimeToExpire(roles.getExpires_in());
			tokenDetails.setTokenValid(roles.getValidToken());
			tokenDetails.setEmail(roles.getEmail());
		}
		RoleBasedAuthToken tokenResponse = new RoleBasedAuthToken(name, authentication.getCredentials().toString(),
				getPermissions(roles));
		tokenResponse.setCustomuserDetails(userDetails);
		if (null != roles) {
			tokenResponse.setRoles(roles.getRolesAsCommaSeperatedString());
		}
		tokenResponse.setAdditional(tokenDetails);
		return tokenResponse;
	}

	/**
	 * Convert the comma separated permission in list
	 * 
	 * @param roles
	 * @return
	 */
	private List<String> getPermissionsList(Roles roles) {

		if (null != roles && !StringUtils.isEmpty(roles.getScope())) {
			String permissions = roles.getScope();
			return Arrays.asList(permissions.split(","));
		}
		return new ArrayList<>();
	}

	/**
	 * Covert the permissions in GrantedAuthority list for the JWT enhancement
	 * 
	 * @param roles
	 * @return
	 */
	private List<GrantedAuthority> getPermissions(Roles roles) {
		List<String> permissions = getPermissionsList(roles);
		return permissions.stream().map(mapToItem).collect(Collectors.toList());
	}

	Function<String, GrantedAuthority> mapToItem = a -> {
		return new GrantedAuthority() {
			private static final long serialVersionUID = 1L;

			@Override
			public String getAuthority() {
				return a;
			}
		};
	};

	private Function<ClientDetailsEntity, ClientDetails> entityToModel = entity -> {
		ClientDetails details = new ClientDetails();
		details.setCorpCode(entity.getCorpCode());
		details.setClientNumber(entity.getClientNumber());
		return details;
	};

	@Override
	public boolean supports(Class<?> authentication) {
		return authentication.equals(UsernamePasswordAuthenticationToken.class);
	}

	/**
	 * Fetch the client details from security database 2.5
	 * 
	 * @param userName
	 * @return
	 */
	private List<ClientDetailsEntity> getClientDetails(String userName) {
		return clientDetailsService.getClientDetails(userName);
	}

}
