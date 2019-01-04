package me.anichakra.poc.gateway.config;

import java.util.List;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * This class is useful for access the Url list from yml
 * 
 * @author MTakate
 *
 */
@ConfigurationProperties(prefix = "conditional")
@Configuration
public class UrlConfig {

	private List<String> preFilterList;

	private List<String> postFilterList;

	private List<String> unauthorizedUrlList;

	private String unauthorizedUrlAccessMessage;

	public List<String> getPreFilterList() {
		return preFilterList;
	}

	public void setPreFilterList(List<String> preFilterList) {
		this.preFilterList = preFilterList;
	}

	public List<String> getPostFilterList() {
		return postFilterList;
	}

	public void setPostFilterList(List<String> postFilterList) {
		this.postFilterList = postFilterList;
	}

	public List<String> getUnauthorizedUrlList() {
		return unauthorizedUrlList;
	}

	public void setUnauthorizedUrlList(List<String> unauthorizedUrlList) {
		this.unauthorizedUrlList = unauthorizedUrlList;
	}

	public String getUnauthorizedUrlAccessMessage() {
		return unauthorizedUrlAccessMessage;
	}

	public void setUnauthorizedUrlAccessMessage(String unauthorizedUrlAccessMessage) {
		this.unauthorizedUrlAccessMessage = unauthorizedUrlAccessMessage;
	}

}
