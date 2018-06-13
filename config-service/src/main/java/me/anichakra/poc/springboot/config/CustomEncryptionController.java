package me.anichakra.poc.springboot.config;

import org.springframework.cloud.config.server.encryption.EncryptionController;
import org.springframework.cloud.config.server.encryption.TextEncryptorLocator;
import org.springframework.context.annotation.Primary;
import org.springframework.http.MediaType;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
@Primary
@RestController
@RequestMapping(path = "${spring.cloud.config.server.prefix:}")
public class CustomEncryptionController extends EncryptionController {

	

	public CustomEncryptionController(TextEncryptorLocator encryptor) {
		super(encryptor);
		// TODO Auto-generated constructor stub
	}
    @PreAuthorize("#oauth2.hasScope('foo') and #oauth2.hasScope('read')")
	@RequestMapping(value = "encrypt", method = RequestMethod.POST)
	public String encrypt(@RequestBody String data,
			@RequestHeader("Content-Type") MediaType type) {

		return super.encrypt(data, type);
	}
    @PreAuthorize("#oauth2.hasScope('foo') and #oauth2.hasScope('read')")
	@RequestMapping(value = "/encrypt/{name}/{profiles}", method = RequestMethod.POST)
	public String encrypt(@PathVariable String name, @PathVariable String profiles,
			@RequestBody String data, @RequestHeader("Content-Type") MediaType type) {
		return super.encrypt(name, profiles, data, type);
	}
    @PreAuthorize("#oauth2.hasScope('foo') and #oauth2.hasScope('read')")
	@RequestMapping(value = "decrypt", method = RequestMethod.POST)
	public String decrypt(@RequestBody String data,
			@RequestHeader("Content-Type") MediaType type) {

		return super.decrypt(data, type);
	}	
    @PreAuthorize("#oauth2.hasScope('foo') and #oauth2.hasScope('read')")
	@RequestMapping(value = "/decrypt/{name}/{profiles}", method = RequestMethod.POST)
	public String decrypt(@PathVariable String name, @PathVariable String profiles,
			@RequestBody String data, @RequestHeader("Content-Type") MediaType type) {
		return super.decrypt(name, profiles, data, type);
	}

}
