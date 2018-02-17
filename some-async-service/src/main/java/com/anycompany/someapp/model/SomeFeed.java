package com.anycompany.someapp.model;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;

@Entity
public class SomeFeed {

	private int id;
	
	private String orderNo;
	
	private String corpCd;
	
	private String cliNo;
	
	private String bkdn;
	
	private String unitNo;

	
	@Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }
	
	/**
	 * @return the orderNo
	 */
	public String getOrderNo() {
		return orderNo;
	}

	/**
	 * @param orderNo the orderNo to set
	 */
	public void setOrderNo(String orderNo) {
		this.orderNo = orderNo;
	}

	/**
	 * @return the corpCd
	 */
	public String getCorpCd() {
		return corpCd;
	}

	/**
	 * @param corpCd the corpCd to set
	 */
	public void setCorpCd(String corpCd) {
		this.corpCd = corpCd;
	}

	/**
	 * @return the cliNo
	 */
	public String getCliNo() {
		return cliNo;
	}

	/**
	 * @param cliNo the cliNo to set
	 */
	public void setCliNo(String cliNo) {
		this.cliNo = cliNo;
	}

	/**
	 * @return the bkdn
	 */
	public String getBkdn() {
		return bkdn;
	}

	/**
	 * @param bkdn the bkdn to set
	 */
	public void setBkdn(String bkdn) {
		this.bkdn = bkdn;
	}

	/**
	 * @return the unitNo
	 */
	public String getUnitNo() {
		return unitNo;
	}

	/**
	 * @param unitNo the unitNo to set
	 */
	public void setUnitNo(String unitNo) {
		this.unitNo = unitNo;
	}

	/* (non-Javadoc)
	 * @see java.lang.Object#toString()
	 */
	@Override
	public String toString() {
		return "SomeFeedModel [orderNo=" + orderNo + ", corpCd=" + corpCd + ", cliNo=" + cliNo + ", bkdn=" + bkdn
				+ ", unitNo=" + unitNo + "]";
	}
}
