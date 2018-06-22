package me.anichakra.springboot.poc.auth.service;

import java.util.function.Function;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.stereotype.Component;

@Component
public class UsernamePasswordAuthenticationProvider implements AuthenticationProvider {

	@Autowired
	private AuthenticationProviderService authenticationProviderService;

	@Override
	public Authentication authenticate(Authentication authentication) throws AuthenticationException {
		String username = authentication.getName();
		User user = authenticationProviderService.retrieveUser();
		return new UsernamePasswordAuthenticationToken(username, authentication.getCredentials(),
				user.getRoles().stream().map(toGrantedAuthority).collect(Collectors.toList()));

	}

	Function<String, GrantedAuthority> toGrantedAuthority = role -> {
		return new GrantedAuthority() {
			private static final long serialVersionUID = 1L;

			@Override
			public String getAuthority() {
				return role;
			}

		};
	};

	@Override
	public boolean supports(Class<?> authentication) {
		return authentication.equals(UsernamePasswordAuthenticationToken.class);
	}

}
