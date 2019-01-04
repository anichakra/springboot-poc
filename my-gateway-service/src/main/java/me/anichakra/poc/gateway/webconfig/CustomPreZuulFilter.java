package me.anichakra.poc.gateway.webconfig;

import java.util.Optional;

import javax.servlet.http.HttpServletRequest;

import org.apache.commons.codec.digest.DigestUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.codec.Base64;
import org.springframework.stereotype.Component;

import com.netflix.zuul.ZuulFilter;
import com.netflix.zuul.context.RequestContext;

import me.anichakra.poc.gateway.config.UrlConfig;

/**
 * CustomPreZuulFilter implement to customized zuul filter chain
 * 
 * @author MTakate
 *
 */
@Component
public class CustomPreZuulFilter extends ZuulFilter {

	private final Logger logger = LoggerFactory.getLogger(CustomPreZuulFilter.class);

	@Autowired
	JwtTokenParameterConfig jwtTokenParameterConfig;

	@Autowired
	private UrlConfig urlConfig;

	@Override
	public Object run() {
		final RequestContext ctx = RequestContext.getCurrentContext();
		final HttpServletRequest req = ctx.getRequest();
		final String requestURI = req.getRequestURI();
		logger.debug("in zuul filter {}", requestURI);
		// Check for oauth token hit
		if (requestURI.contains("oauth/token")) {
			byte[] encoded;
			try {
				encoded = Base64
						.encode((jwtTokenParameterConfig.getClientId() + ":" + jwtTokenParameterConfig.getSecret())
								.getBytes("UTF-8"));
				ctx.addZuulRequestHeader(jwtTokenParameterConfig.getHeaderAuthorization(),
						"Basic " + new String(encoded));

			} catch (Exception e) {
				throw new RuntimeException(e);
			}
			// check if the url is amongst configured unauthorized URLs
		} else if (checkNonAccessUrls(requestURI)) {
			throw new RuntimeException();
			// check if the url is amongst configured skip URLs
		} else if (skipUrl(requestURI)) {
			String jwtToken = req.getHeader(jwtTokenParameterConfig.getHeaderAuthorization());
			if (null != jwtToken) {
				ctx.addZuulRequestHeader(jwtTokenParameterConfig.getHeaderAuthorization(), jwtToken);
			}
			// for all other conditions
		}

		return null;
	}


	private boolean skipUrl(String url) {
		Optional<String> skipUrl = urlConfig.getPreFilterList().stream().filter(a -> url.contains(a)).findFirst();
		return skipUrl.isPresent();
	}

	private boolean checkNonAccessUrls(String url) {
		Optional<String> nonAccessUrls = urlConfig.getUnauthorizedUrlList().stream().filter(a -> url.contains(a))
				.findFirst();
		return nonAccessUrls.isPresent();
	}

	/**
	 * Validate the cached access_token with client token
	 * 
	 * @param tokenId
	 * @param sessionObject
	 * @return true or false
	 */
	private boolean validateToken(String tokenId, Object sessionObject) {
		String token = String.valueOf(sessionObject);
		return tokenId.equals(DigestUtils.sha256Hex(token));
	}


	@Override
	public boolean shouldFilter() {
		return true;
	}

	@Override
	public int filterOrder() {
		return -2;
	}

	@Override
	public String filterType() {
		return "pre";
	}

}
