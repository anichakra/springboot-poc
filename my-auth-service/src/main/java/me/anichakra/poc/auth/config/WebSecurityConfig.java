package me.anichakra.poc.auth.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.security.SecurityProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.annotation.Order;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.client.RestTemplate;

import me.anichakra.poc.auth.repository.eauth.EauthConfig;
import me.anichakra.poc.auth.service.UsernamePasswordAuthenticationProvider;

/**
 * The first step is to create our Spring Security Java Configuration
 * here configure the basic rest end point and authentication manager for the spring security
 * @author MTakate
 *
 */
@Configuration
@Order(SecurityProperties.ACCESS_OVERRIDE_ORDER)
public class WebSecurityConfig extends WebSecurityConfigurerAdapter {
	
	@Autowired
	private OauthSecurityEndpointConfig oauthSecurityEndpointConfig;
	
	@Autowired
	private UsernamePasswordAuthenticationProvider provider;
	/**
	 * Assign the custom authentication provider to authentication manager builder for the authentication process
	 * @param auth
	 * @throws Exception
	 */
    @Autowired
    public void globalUserDetails(final AuthenticationManagerBuilder auth) throws Exception {
        // @formatter:off
	auth.eraseCredentials(false).authenticationProvider(provider); 
    }// @formatter:on
	
    @Override
    @Bean
    public AuthenticationManager authenticationManagerBean() throws Exception {
        return super.authenticationManagerBean();
    }
    
    @Bean
   	public PasswordEncoder passwordEncoder() {
   		return new BCryptPasswordEncoder();
   	}

    @Bean
	public RestTemplate restTemplate() {
		return new RestTemplate();
	}

	@Bean
	public EauthConfig forgeRockConfig() {
		return new EauthConfig();
	}
	
	@Bean
	public OauthSecurityEndpointConfig getOauthSecurityEndpointConfig() {
		return new OauthSecurityEndpointConfig();				
	}
	/**
	 * Configure the basic Spring Security authentication and rest end points
	 */
    @Override
    protected void configure(final HttpSecurity http) throws Exception {
        // @formatter:off
		http.authorizeRequests().antMatchers(oauthSecurityEndpointConfig.getLogin()).permitAll()
		.antMatchers(oauthSecurityEndpointConfig.getRevokeById()).permitAll()
		.antMatchers(oauthSecurityEndpointConfig.getTokens()).permitAll()
		.anyRequest().authenticated()
		.and().formLogin().permitAll()
		.and().csrf().disable();
		// @formatter:on
    }

}
