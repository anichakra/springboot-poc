package me.anichakra.poc.auth.repository.eauth;

import org.springframework.boot.context.properties.ConfigurationProperties;
/**
 * Eauth configuration class using for forge rock request parameter 
 * @author MTakate
 *
 */
@ConfigurationProperties(prefix="forgeRock")
public class EauthConfig {

    private String appNameKey;
    
    private String appNameValue;
    
    private String appTokenKey;
    
    private String appTokenValue;
    
    private String grantTypeKey;
    
    private String grantTypeValue;
    
    private String cliIdKey;
    
    private String cliIdValue;
    
    private String cliSecretKey;
    
    private String cliSecretValue;
    
    private String scopeKey;
    
    private String scopeValue;
    
    private String userKey;
    
    private String prwdKey;

    private String authUrl;
    
    private String permissionUrl;
    
	public String getAuthUrl() {
		return authUrl;
	}

	public void setAuthUrl(String authUrl) {
		this.authUrl = authUrl;
	}

	public String getPermissionUrl() {
		return permissionUrl;
	}

	public void setPermissionUrl(String permissionUrl) {
		this.permissionUrl = permissionUrl;
	}

	public String getAppNameKey() {
		return appNameKey;
	}

	public void setAppNameKey(String appNameKey) {
		this.appNameKey = appNameKey;
	}

	public String getAppNameValue() {
		return appNameValue;
	}

	public void setAppNameValue(String appNameValue) {
		this.appNameValue = appNameValue;
	}

	public String getAppTokenKey() {
		return appTokenKey;
	}

	public void setAppTokenKey(String appTokenKey) {
		this.appTokenKey = appTokenKey;
	}

	public String getAppTokenValue() {
		return appTokenValue;
	}

	public void setAppTokenValue(String appTokenValue) {
		this.appTokenValue = appTokenValue;
	}

	public String getGrantTypeKey() {
		return grantTypeKey;
	}

	public void setGrantTypeKey(String grantTypeKey) {
		this.grantTypeKey = grantTypeKey;
	}

	public String getGrantTypeValue() {
		return grantTypeValue;
	}

	public void setGrantTypeValue(String grantTypeValue) {
		this.grantTypeValue = grantTypeValue;
	}

	public String getCliIdKey() {
		return cliIdKey;
	}

	public void setCliIdKey(String cliIdKey) {
		this.cliIdKey = cliIdKey;
	}

	public String getCliIdValue() {
		return cliIdValue;
	}

	public void setCliIdValue(String cliIdValue) {
		this.cliIdValue = cliIdValue;
	}

	public String getCliSecretKey() {
		return cliSecretKey;
	}

	public void setCliSecretKey(String cliSecretKey) {
		this.cliSecretKey = cliSecretKey;
	}

	public String getCliSecretValue() {
		return cliSecretValue;
	}

	public void setCliSecretValue(String cliSecretValue) {
		this.cliSecretValue = cliSecretValue;
	}

	public String getScopeKey() {
		return scopeKey;
	}

	public void setScopeKey(String scopeKey) {
		this.scopeKey = scopeKey;
	}

	public String getScopeValue() {
		return scopeValue;
	}

	public void setScopeValue(String scopeValue) {
		this.scopeValue = scopeValue;
	}
	
	public String getUserKey() {
		return userKey;
	}

	public void setUserKey(String userKey) {
		this.userKey = userKey;
	}
	

	public String getPrwdKey() {
		return prwdKey;
	}

	public void setPrwdKey(String prwdKey) {
		this.prwdKey = prwdKey;
	}
}
