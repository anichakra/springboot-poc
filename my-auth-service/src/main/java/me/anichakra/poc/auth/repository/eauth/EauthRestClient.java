package me.anichakra.poc.auth.repository.eauth;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

import me.anichakra.poc.common.EauthResponse;
import me.anichakra.poc.common.Roles;
/**
 * EauthRestClient class used to authenticate the user from forge rock and fetch the permission to respective user.
 * @author MTakate
 *
 */
@Component
public class EauthRestClient {

	@Autowired
	@Qualifier("restTemplate")
	RestTemplate restTemplate;

	@Autowired
	private EauthConfig forgeRockConfig;
	
	/**
	 * This method is actually used for the authentication of the user with username and password from forge rock
	 * @param authentication
	 * @return access_token after successful authentication
	 */
	public EauthResponse getForgerockToken(Authentication authentication) {

		MultiValueMap<String, String> map = new LinkedMultiValueMap<>();
		map.add(forgeRockConfig.getGrantTypeKey(), forgeRockConfig.getGrantTypeValue());
		map.add(forgeRockConfig.getCliIdKey(), forgeRockConfig.getCliIdValue());
		map.add(forgeRockConfig.getCliSecretKey(), forgeRockConfig.getCliSecretValue());
		map.add(forgeRockConfig.getUserKey(), authentication.getName());
		map.add(forgeRockConfig.getPrwdKey(), authentication.getCredentials().toString());
		map.add(forgeRockConfig.getScopeKey(), forgeRockConfig.getScopeValue());

		HttpEntity<MultiValueMap<String, String>> request = new HttpEntity<>(map,getHttpHeaders());
		ResponseEntity<EauthResponse> respEntity = restTemplate.postForEntity(forgeRockConfig.getAuthUrl(), request,EauthResponse.class);
		return respEntity.getBody();
	}
	/**
	 * This method used to fetch the authenticated user permissions and basic user details
	 * @param token
	 * @return return permissions and basic user details in roles object
	 */
	public Roles getPermissions(String token) {
		MultiValueMap<String, String> map = new LinkedMultiValueMap<>();
		HttpEntity<MultiValueMap<String, String>> request = new HttpEntity<>(map,getHttpHeaders());
		ResponseEntity<Roles> respEntity = restTemplate.postForEntity(forgeRockConfig.getPermissionUrl() + token,request, Roles.class);
		return respEntity.getBody();
	}
	/**
	 * This method is used to build the header for the forge rock request
	 * @return
	 */
	public HttpHeaders getHttpHeaders() {
		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);
		headers.set(forgeRockConfig.getAppNameKey(), forgeRockConfig.getAppNameValue());
		headers.set(forgeRockConfig.getAppTokenKey(), forgeRockConfig.getAppTokenValue());
		return headers;
	}
}
