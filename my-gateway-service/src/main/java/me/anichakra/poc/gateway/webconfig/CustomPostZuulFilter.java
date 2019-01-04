package me.anichakra.poc.gateway.webconfig;

import java.io.IOException;
import java.io.InputStream;

import org.apache.commons.codec.digest.DigestUtils;
import org.apache.commons.io.IOUtils;
import org.springframework.stereotype.Component;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.netflix.zuul.ZuulFilter;
import com.netflix.zuul.context.RequestContext;

/**
 * PostZuul filter  include adding standard HTTP headers to the response, gathering statistics and metrics,
 * and streaming the response from the origin to the client.
 * @author MTakate
 *
 */
@Component
public class CustomPostZuulFilter extends ZuulFilter {

	private ObjectMapper mapper;

	/**
	 * Customizing the response of the request 
	 */
	@Override
	public Object run() {
		final RequestContext ctx = RequestContext.getCurrentContext();
		final String requestURI = ctx.getRequest().getRequestURI();
		try {
			
			final InputStream is = ctx.getResponseDataStream();
			String responseBody = IOUtils.toString(is, "UTF-8");

			if (requestURI.contains("/oauth/token")) {
				// Call when url contains /oauth/token
				if (null != responseBody && responseBody.contains("access_token")) {
					// Call when response body having good response
					AccessTokenMapper accessTokenMapper = getMapper().readValue(responseBody, AccessTokenMapper.class);

					String accessToken = DigestUtils.sha256Hex(accessTokenMapper.getAccess_token());
					String refreshToken = DigestUtils.sha256Hex(accessTokenMapper.getRefresh_token());

					accessTokenMapper.setAccess_token(accessToken);
					accessTokenMapper.setRefresh_token(refreshToken);
					responseBody = mapper.writeValueAsString(accessTokenMapper);
				}
			}
			ctx.setResponseBody(responseBody);
		} catch (final IOException e) {
			throw new RuntimeException(e);
		}
		return null;
	}
	

	@Override
	public boolean shouldFilter() {
		return true;
	}

	@Override
	public int filterOrder() {
		return 10;
	}

	@Override
	public String filterType() {
		return "post";
	}

	public ObjectMapper getMapper() {
		if (mapper == null) {
			mapper = new ObjectMapper();
		}
		return mapper;
	}

	public void setMapper(ObjectMapper mapper) {
		this.mapper = mapper;
	}

}
