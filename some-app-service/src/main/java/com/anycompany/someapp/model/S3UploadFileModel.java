package com.anycompany.someapp.model;

import java.io.ByteArrayInputStream;
import java.util.Map;

public class S3UploadFileModel {

	private String fileName;
	
	private ByteArrayInputStream inputStream;
	
	private Map<String, String> metadata;

	public S3UploadFileModel(String fileName, byte[] inputStream, Map<String, String> metadata) {
		super();
		this.fileName = fileName;
		this.inputStream = new ByteArrayInputStream(inputStream);
		this.metadata = metadata;
	}

	/**
	 * @return the fileName
	 */
	public String getFileName() {
		return fileName;
	}

	/**
	 * @param fileName the fileName to set
	 */
	public void setFileName(String fileName) {
		this.fileName = fileName;
	}

	/**
	 * @return the inputStream
	 */
	public ByteArrayInputStream getInputStream() {
		return inputStream;
	}

	/**
	 * @param inputStream the inputStream to set
	 */
	public void setInputStream(byte[] inputStream) {
		this.inputStream = new ByteArrayInputStream(inputStream);
	}

	/**
	 * @return the metadata
	 */
	public Map<String, String> getMetadata() {
		return metadata;
	}

	/**
	 * @param metadata the metadata to set
	 */
	public void setMetadata(Map<String, String> metadata) {
		this.metadata = metadata;
	}
	
	
	
}
