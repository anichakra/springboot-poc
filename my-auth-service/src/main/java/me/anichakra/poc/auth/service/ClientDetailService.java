package me.anichakra.poc.auth.service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import me.anichakra.poc.auth.domain.ClientDetailsEntity;
import me.anichakra.poc.auth.repository.ClientDetailRepository;

@Service
public class ClientDetailService {

	@Autowired
	private ClientDetailRepository clientDetailsRepository;
	/**
	 * Fetching clinet numbber and corp code from security database by using login id as parameter
	 * @param login
	 * @return
	 */
	public List<ClientDetailsEntity> getClientDetails(String id) {
		return  clientDetailsRepository.findClientNumberAndCorpCodeByLogin(id);
	}
}