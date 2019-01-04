package me.anichakra.poc.auth.repository;

import java.util.List;

import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

import me.anichakra.poc.auth.domain.ClientDetailsEntity;

@Repository
public interface ClientDetailRepository extends CrudRepository<ClientDetailsEntity, Integer> {
	/**
	 * Fetching clinet numbber and corp code from security database by using login id as parameter
	 * @param login
	 * @return
	 */
	List<ClientDetailsEntity> findClientNumberAndCorpCodeByLogin(String login);
}
