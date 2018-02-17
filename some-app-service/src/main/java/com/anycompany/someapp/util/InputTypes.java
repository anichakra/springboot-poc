package com.anycompany.someapp.util;

public enum InputTypes {

	SOME_FEED("some-async-service");

	private String serviceType;

	/**
	 * @param serviceType
	 *            the serviceType to set
	 */
	InputTypes(String serviceType) {
		this.serviceType = serviceType;
	}

	/**
	 * @return the serviceType
	 */
	public String type() {
		return serviceType;
	}

	public static InputTypes getInstance(String serviceType) {
		return InputTypes.valueOf(serviceType);
	}

}
