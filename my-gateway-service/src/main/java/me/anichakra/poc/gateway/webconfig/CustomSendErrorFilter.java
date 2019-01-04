package me.anichakra.poc.gateway.webconfig;

import javax.servlet.RequestDispatcher;
import javax.servlet.http.HttpServletRequest;

import org.springframework.cloud.netflix.zuul.filters.post.SendErrorFilter;
import org.springframework.context.annotation.Configuration;
import org.springframework.util.ReflectionUtils;

import com.netflix.zuul.context.RequestContext;

@Configuration
public class CustomSendErrorFilter extends SendErrorFilter {

	@Override
	public Object run() {
		try {
			RequestContext ctx = RequestContext.getCurrentContext();
			HttpServletRequest request = ctx.getRequest();
			request.setAttribute("javax.servlet.error.status_code", 500);
			request.setAttribute("javax.servlet.error.message",
					"Error while getting response, Please try again after sometime or contact administrator");
			RequestDispatcher dispatcher = request.getRequestDispatcher("/error");
			if (dispatcher != null) {
				ctx.set(SEND_ERROR_FILTER_RAN, true);
				if (!ctx.getResponse().isCommitted()) {
					ctx.setResponseStatusCode(500);
					dispatcher.forward(request, ctx.getResponse());
				}
			}
		} catch (Exception ex) {
			ReflectionUtils.rethrowRuntimeException(ex);
		}
		return null;
	}

}
