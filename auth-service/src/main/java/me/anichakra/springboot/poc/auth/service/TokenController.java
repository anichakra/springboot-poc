package me.anichakra.springboot.poc.auth.service;

import java.util.Optional;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.oauth2.common.OAuth2AccessToken;
import org.springframework.security.oauth2.provider.OAuth2Authentication;
import org.springframework.security.oauth2.provider.token.ConsumerTokenServices;
import org.springframework.security.oauth2.provider.token.TokenStore;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
public class TokenController {

	@Autowired
	private TokenCacheService tokenCacheService;

	@Resource(name = "tokenServices")
	ConsumerTokenServices tokenServices;

	@Resource(name = "tokenStore")
	TokenStore tokenStore;

	@PostMapping("/oauth/token/revokeById/{tokenId}")
	@ResponseBody
	public ResponseEntity<HttpStatus> revokeToken(HttpServletRequest request, @PathVariable String tokenId) {
		tokenServices.revokeToken(tokenId);
		//TODO: to handle exception and return proper status
		return new ResponseEntity<HttpStatus>(HttpStatus.OK);
	}

	@PreAuthorize("#oauth2.hasScope('ADMIN')")
    @PostMapping(value = "/tokens/revokeByUsername/{username}")
    @ResponseBody
    public ResponseEntity<HttpStatus> revokeToken(@PathVariable String username) {
    	OAuth2AccessToken accessToken =  (OAuth2AccessToken) tokenCacheService.getAccessToken();
        Optional<OAuth2AccessToken> accessToken_opt = Optional.ofNullable(accessToken);
        accessToken_opt.ifPresent(a->{
        	Optional.ofNullable(a.getRefreshToken()).ifPresent(b->revokeRefreshToken(b.getValue()));
        	revokeToken(a.getValue());
        });
		//TODO: to handle exception and return proper status

        return new ResponseEntity<HttpStatus>(HttpStatus.OK);
    }

	@PostMapping("/tokens/revokeRefreshToken/{tokenId:.*}")
	@ResponseBody
	public ResponseEntity<HttpStatus> revokeRefreshToken(@PathVariable String tokenId) {
		Optional.ofNullable(tokenId).ifPresent(a -> {
			OAuth2Authentication authentication = tokenStore.readAuthentication(tokenId);
			tokenCacheService.remove(authentication.getName());
		});
		//TODO: to handle exception and return proper status

		return new ResponseEntity<HttpStatus>(HttpStatus.OK);
	}

}