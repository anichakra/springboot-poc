package me.anichakra.poc.auth.service;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.oauth2.common.DefaultOAuth2AccessToken;
import org.springframework.security.oauth2.common.OAuth2AccessToken;
import org.springframework.security.oauth2.provider.OAuth2Authentication;
import org.springframework.security.oauth2.provider.token.TokenEnhancer;
import org.springframework.security.web.authentication.preauth.PreAuthenticatedAuthenticationToken;

/**
 * JwtEnhancer used to enhance the our JSON Web Token as per the requirement
 * @author MTakate
 *
 */
public class JwtEnhancer implements TokenEnhancer {

	@Autowired
	private TokenCacheService tokenCacheService;
	
	/**
	 * This method enhance the JSON Web Token by adding the additional information in JWT.
	 */
	@Override
	public OAuth2AccessToken enhance(OAuth2AccessToken accessToken, OAuth2Authentication authentication) {
		final Map<String, Object> additionalInfo = new HashMap<>();
		Set<String> scope = authentication.getUserAuthentication().getAuthorities().stream()
				.map(GrantedAuthority::getAuthority).collect(Collectors.toSet());
		Authentication userAuthentication = authentication.getUserAuthentication();
		if (userAuthentication instanceof RoleBasedAuthToken) {
			// This is calling at authentication using username and password
			RoleBasedAuthToken customToken = ((RoleBasedAuthToken) authentication.getUserAuthentication());
			additionalInfo.put("additionalDetails", customToken.getAdditional());
			additionalInfo.put("scope", StringUtils.join(scope, " "));
			additionalInfo.put("userDetails", customToken.getCustomuserDetails());

			if (accessToken instanceof DefaultOAuth2AccessToken)
				((DefaultOAuth2AccessToken) accessToken).setAdditionalInformation(additionalInfo);
		}
		if (userAuthentication instanceof PreAuthenticatedAuthenticationToken) {
			// This is calling at refresh token generation
			Object o = tokenCacheService.get(userAuthentication.getName().toLowerCase());
			if (o instanceof OAuth2AccessToken) {
				OAuth2AccessToken token = (OAuth2AccessToken) o;
				Map<String, Object> additionalInfoMap = token.getAdditionalInformation();
				me.anichakra.poc.common.security.UserDetails ud = (me.anichakra.poc.common.security.UserDetails) additionalInfoMap
						.get("userDetails");

				additionalInfo.put("scope", StringUtils.join(scope, " "));
				additionalInfo.put("userDetails", ud);

				if (accessToken instanceof DefaultOAuth2AccessToken)
					((DefaultOAuth2AccessToken) accessToken).setAdditionalInformation(additionalInfo);
			}
		}
		return accessToken;
	}
}
