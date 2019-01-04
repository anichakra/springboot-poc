package me.anichakra.poc.auth.service;

import java.io.IOException;
import java.util.Arrays;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.DefaultResourceLoader;
import org.springframework.core.io.Resource;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.method.configuration.EnableGlobalMethodSecurity;
import org.springframework.security.oauth2.config.annotation.configurers.ClientDetailsServiceConfigurer;
import org.springframework.security.oauth2.config.annotation.web.configuration.AuthorizationServerConfigurerAdapter;
import org.springframework.security.oauth2.config.annotation.web.configuration.EnableAuthorizationServer;
import org.springframework.security.oauth2.config.annotation.web.configurers.AuthorizationServerEndpointsConfigurer;
import org.springframework.security.oauth2.config.annotation.web.configurers.AuthorizationServerSecurityConfigurer;
import org.springframework.security.oauth2.provider.token.DefaultTokenServices;
import org.springframework.security.oauth2.provider.token.TokenEnhancer;
import org.springframework.security.oauth2.provider.token.TokenEnhancerChain;
import org.springframework.security.oauth2.provider.token.TokenStore;
import org.springframework.security.oauth2.provider.token.store.JwtAccessTokenConverter;
import org.springframework.security.oauth2.provider.token.store.KeyStoreKeyFactory;

import me.anichakra.poc.auth.config.JwtTokenParameterConfig;
/**
 * This class is used as Authorization server for the JWT
 * @author MTakate
 *
 */
@Configuration
@EnableAuthorizationServer
@EnableGlobalMethodSecurity
public class OAuth2AuthorizationServerConfigJwt extends AuthorizationServerConfigurerAdapter {

	@Autowired
	JwtTokenParameterConfig tokenParameterConfig;
	
    @Autowired
    @Qualifier("authenticationManagerBean")
    private AuthenticationManager authenticationManager;
    
    @Override
    public void configure(final AuthorizationServerSecurityConfigurer oauthServer) throws Exception {
        oauthServer.tokenKeyAccess("permitAll()")
            .checkTokenAccess("isAuthenticated()");
    }
    /**
     * This method used to config client for the JWT
     */
    @Override
    public void configure(final ClientDetailsServiceConfigurer clients) throws Exception {
        clients.inMemory()
            .withClient(tokenParameterConfig.getClientId())
            .secret(tokenParameterConfig.getSecret())
            .authorizedGrantTypes(tokenParameterConfig.getGrandTypePrwd(), tokenParameterConfig.getGrandTypeAuthorizationCode(), tokenParameterConfig.getGrnadTypeRefreshToken())
            .scopes(tokenParameterConfig.getScopes())
            .accessTokenValiditySeconds(tokenParameterConfig.getAccessTokenValidity())
            .refreshTokenValiditySeconds(tokenParameterConfig.getRefreshTokenValidity())
            .and()
            .withClient(tokenParameterConfig.getAutosysClientId())
            .secret(tokenParameterConfig.getAutosysSecret())
            .authorizedGrantTypes(tokenParameterConfig.getGrandTypePrwd(), tokenParameterConfig.getGrandTypeAuthorizationCode(), tokenParameterConfig.getGrnadTypeRefreshToken())
            .scopes(tokenParameterConfig.getScopes())
            .accessTokenValiditySeconds(tokenParameterConfig.getAutosysAccessTokenValidity())
            .refreshTokenValiditySeconds(tokenParameterConfig.getAutosysRefreshTokenValidity())
        ;
    }

    @Bean
    @Primary
    public DefaultTokenServices tokenServices() {
        final DefaultTokenServices defaultTokenServices = new DefaultTokenServices();
        defaultTokenServices.setTokenStore(tokenStore());
        defaultTokenServices.setSupportRefreshToken(true);
        return defaultTokenServices;
    }

    @Override
    public void configure(final AuthorizationServerEndpointsConfigurer endpoints) throws Exception {
        final TokenEnhancerChain tokenEnhancerChain = new TokenEnhancerChain();
        tokenEnhancerChain.setTokenEnhancers(Arrays.asList(tokenEnhancer(), accessTokenConverter()));
        endpoints.tokenStore(tokenStore())
            .tokenEnhancer(tokenEnhancerChain)
            .authenticationManager(authenticationManager).accessTokenConverter(accessTokenConverter());
    }

    @Bean
    public TokenStore tokenStore() {
        return new JwtCache(accessTokenConverter());
    }
    /**
     * Creates bean of accessTokenConverter
     * @return
     */
    @Bean
    public JwtAccessTokenConverter accessTokenConverter() {
        final JwtAccessTokenConverter converter = new JwtAccessTokenConverter();
        DefaultResourceLoader loader = new DefaultResourceLoader();
        final KeyStoreKeyFactory keyStoreKeyFactory = new KeyStoreKeyFactory(loader.getResource(tokenParameterConfig.getJksPath()), tokenParameterConfig.getKeyPass().toCharArray());
        converter.setKeyPair(keyStoreKeyFactory.getKeyPair(tokenParameterConfig.getKeyPair()));
        
        final Resource resource = new ClassPathResource("public.txt");
		String publicKey = null;
		try {
			publicKey = org.apache.commons.io.IOUtils.toString(resource.getInputStream());
		} catch (final IOException e) {
			throw new RuntimeException(e);
		}
		converter.setVerifierKey(publicKey);
        
        return converter;
    }

    @Bean
    public TokenEnhancer tokenEnhancer() {
        return new JwtEnhancer();
    }
}
