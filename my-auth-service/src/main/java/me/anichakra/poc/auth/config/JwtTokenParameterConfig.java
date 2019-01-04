package me.anichakra.poc.auth.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * JOSN Web Token parameter to build the JWT 
 * @author MTakate
 *
 */
@Configuration
@ConfigurationProperties(prefix="jwtToken.parameter")
public class JwtTokenParameterConfig {

	private String clientId;
	private String secret;
	private String grandTypePrwd;
	private String grandTypeAuthorizationCode;
	private String grnadTypeRefreshToken;
	private String scopes;
    private int accessTokenValidity;
    private int refreshTokenValidity;
    private String grantType;
    private String refreshToken;
    private String headerRefreshToken;
    private String headerAuthorization;
	private String jksPath;
	private String keyPass;
	private String keyPair;
	private String autosysClientId;
    private String autosysSecret;    
    private int autosysAccessTokenValidity;
    private int autosysRefreshTokenValidity;
    
	public String getClientId() {
		return clientId;
	}
	public void setClientId(String clientId) {
		this.clientId = clientId;
	}
	public String getSecret() {
		return secret;
	}
	public void setSecret(String secret) {
		this.secret = secret;
	}

	public String getGrandTypePrwd() {
		return grandTypePrwd;
	}
	public void setGrandTypePrwd(String grandTypePrwd) {
		this.grandTypePrwd = grandTypePrwd;
	}
	public String getGrandTypeAuthorizationCode() {
		return grandTypeAuthorizationCode;
	}
	public void setGrandTypeAuthorizationCode(String grandTypeAuthorizationCode) {
		this.grandTypeAuthorizationCode = grandTypeAuthorizationCode;
	}
	public String getGrnadTypeRefreshToken() {
		return grnadTypeRefreshToken;
	}
	public void setGrnadTypeRefreshToken(String grnadTypeRefreshToken) {
		this.grnadTypeRefreshToken = grnadTypeRefreshToken;
	}
	public String getScopes() {
		return scopes;
	}
	public void setScopes(String scopes) {
		this.scopes = scopes;
	}
	public int getAccessTokenValidity() {
		return accessTokenValidity;
	}
	public void setAccessTokenValidity(int accessTokenValidity) {
		this.accessTokenValidity = accessTokenValidity;
	}
	public int getRefreshTokenValidity() {
		return refreshTokenValidity;
	}
	public void setRefreshTokenValidity(int refreshTokenValidity) {
		this.refreshTokenValidity = refreshTokenValidity;
	}
	public String getGrantType() {
		return grantType;
	}
	public void setGrantType(String grantType) {
		this.grantType = grantType;
	}
	public String getRefreshToken() {
		return refreshToken;
	}
	public void setRefreshToken(String refreshToken) {
		this.refreshToken = refreshToken;
	}
	public String getHeaderRefreshToken() {
		return headerRefreshToken;
	}
	public void setHeaderRefreshToken(String headerRefreshToken) {
		this.headerRefreshToken = headerRefreshToken;
	}
	public String getHeaderAuthorization() {
		return headerAuthorization;
	}
	public void setHeaderAuthorization(String headerAuthorization) {
		this.headerAuthorization = headerAuthorization;
	}
	public String getJksPath() {
		return jksPath;
	}
	public void setJksPath(String jksPath) {
		this.jksPath = jksPath;
	}
	public String getKeyPass() {
		return keyPass;
	}
	public void setKeyPass(String keyPass) {
		this.keyPass = keyPass;
	}
	public String getKeyPair() {
		return keyPair;
	}
	public void setKeyPair(String keyPair) {
		this.keyPair = keyPair;
	}
	public String getAutosysClientId() {
		return autosysClientId;
	}
	public void setAutosysClientId(String autosysClientId) {
		this.autosysClientId = autosysClientId;
	}
	public String getAutosysSecret() {
		return autosysSecret;
	}
	public void setAutosysSecret(String autosysSecret) {
		this.autosysSecret = autosysSecret;
	}
	public int getAutosysAccessTokenValidity() {
		return autosysAccessTokenValidity;
	}
	public void setAutosysAccessTokenValidity(int autosysAccessTokenValidity) {
		this.autosysAccessTokenValidity = autosysAccessTokenValidity;
	}
	public int getAutosysRefreshTokenValidity() {
		return autosysRefreshTokenValidity;
	}
	public void setAutosysRefreshTokenValidity(int autosysRefreshTokenValidity) {
		this.autosysRefreshTokenValidity = autosysRefreshTokenValidity;
	}
}
