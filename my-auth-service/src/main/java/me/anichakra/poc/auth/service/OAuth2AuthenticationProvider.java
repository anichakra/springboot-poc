package me.anichakra.poc.auth.service;

import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.authentication.configurers.GlobalAuthenticationConfigurerAdapter;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.common.OAuth2AccessToken;
/**
 * OAuth2AuthenticationProvider used for the authentication process during the refresh token generation 
 * @author MTakate
 *
 */
@Configuration
public class OAuth2AuthenticationProvider extends GlobalAuthenticationConfigurerAdapter {

	@Autowired
	private PasswordEncoder passwordEncoder;

	@Autowired
	TokenCacheService cacheService;

	/**
	 * This class used in the process of refresh token creation
	 * @author MTakate
	 *
	 */
	public static class LocalUserDetails implements UserDetails {

		private static final long serialVersionUID = 1L;
		private me.anichakra.poc.common.security.UserDetails ud;

		public LocalUserDetails(me.anichakra.poc.common.security.UserDetails ud) {
			this.ud = ud;
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

		@Override
		public Collection<? extends GrantedAuthority> getAuthorities() {
			if (null != ud) {
				List<String> permissions = ud.getPermissions();

				if (null != permissions) {
					return permissions.stream().map(mapToItem).collect(Collectors.toList());
				}
			}
			return null;
		}

		@Override
		public String getPassword() {
			return null;
		}

		@Override
		public String getUsername() {
			
			return Optional.ofNullable(ud.getLogin().toLowerCase()).orElse("");
		}

		@Override
		public boolean isAccountNonExpired() {
			if(null == ud) {
				return false;
			}
			return true;
		}

		@Override
		public boolean isAccountNonLocked() {
			return true;
		}

		@Override
		public boolean isCredentialsNonExpired() {
			return true;
		}

		@Override
		public boolean isEnabled() {
			return true;
		}
	}
	/**
	 * This method used to load the client details from OAuth2AccessToken to LocalUserDetails for refresh token creation
	 */
	@Override
	public void init(AuthenticationManagerBuilder auth) throws Exception {
		auth.userDetailsService(new UserDetailsService() {

			@Override
			public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {

				Object o = cacheService.get(username.toLowerCase());
				if (o instanceof OAuth2AccessToken) {
					OAuth2AccessToken token = (OAuth2AccessToken) o;
					Map<String, Object> additionalInfo = token.getAdditionalInformation();
					me.anichakra.poc.common.security.UserDetails ud = (me.anichakra.poc.common.security.UserDetails) additionalInfo
							.get("userDetails");
					return new LocalUserDetails(ud);

				}else {
					return new LocalUserDetails(null);
				}
			}
		}).passwordEncoder(passwordEncoder);
	}
}
