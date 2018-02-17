package com.anycompany.someapp.model;

import java.io.InputStream;
import java.util.Map;

public class S3UploadFileModel {

	private String fileName;
	
	private InputStream inputStream;
	
	private Map<String, String> metadata;

	public S3UploadFileModel(String fileName, InputStream inputStream, Map<String, String> metadata) {
		super();
		this.fileName = fileName;
		this.inputStream = inputStream;
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
	public InputStream getInputStream() {
		return inputStream;
	}

	/**
	 * @param inputStream the inputStream to set
	 */
	public void setInputStream(InputStream inputStream) {
		this.inputStream = inputStream;
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
