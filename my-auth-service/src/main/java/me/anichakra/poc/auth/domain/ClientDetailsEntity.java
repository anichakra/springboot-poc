package me.anichakra.poc.auth.domain;

import java.sql.Timestamp;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;
/**
 * Entity class for the client details from security database.
 * @author MTakate
 *
 */
@Entity
@Table(name = "PHH_LOGIN_ACCESS", catalog = "spin_north_america_i2", schema = "dbo")
public class ClientDetailsEntity {

	@Column(name = "login") 
	private String login;

	@Column(name = "corp_cd")
	private String corpCode;

	@Id
	@Column(name = "cli_no")
	private String clientNumber;

	@Column(name = "bkdn")
	private String bkdn;

	@Column(name = "audit_insert_date")
	private Timestamp auditInsertDate;

	@Column(name = "audit_update_date")
	private Timestamp auditUpdateDate;

	@Column(name = "audit_insert_login")
	private String auditInsertLogin;

	@Column(name = "audit_update_login")
	private String auditUpdateLogin;

	public String getLogin() {
		return login;
	}

	public void setLogin(String login) {
		this.login = login;
	}

	public String getCorpCode() {
		return corpCode;
	}

	public void setCorpCode(String corpCode) {
		this.corpCode = corpCode;
	}

	public String getClientNumber() {
		return clientNumber;
	}

	public void setClientNumber(String clientNumber) {
		this.clientNumber = clientNumber;
	}

	public String getBkdn() {
		return bkdn;
	}

	public void setBkdn(String bkdn) {
		this.bkdn = bkdn;
	}

	public Timestamp getAuditInsertDate() {
		return auditInsertDate;
	}

	public void setAuditInsertDate(Timestamp auditInsertDate) {
		this.auditInsertDate = auditInsertDate;
	}

	public Timestamp getAuditUpdateDate() {
		return auditUpdateDate;
	}

	public void setAuditUpdateDate(Timestamp auditUpdateDate) {
		this.auditUpdateDate = auditUpdateDate;
	}

	public String getAuditInsertLogin() {
		return auditInsertLogin;
	}

	public void setAuditInsertLogin(String auditInsertLogin) {
		this.auditInsertLogin = auditInsertLogin;
	}

	public String getAuditUpdateLogin() {
		return auditUpdateLogin;
	}

	public void setAuditUpdateLogin(String auditUpdateLogin) {
		this.auditUpdateLogin = auditUpdateLogin;
	}
}
