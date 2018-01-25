package com.anycompany.someapp.s3;

import java.io.InputStream;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.GetObjectRequest;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.PutObjectRequest;
import com.amazonaws.services.s3.model.S3Object;
import com.anycompany.someapp.model.S3UploadFileModel;

@Component
public class S3Actions {

	@Autowired
	private AmazonS3 s3;

	@Value("${amazon.bucketName}")
	private String bucketName;

	public String postFileToS3(S3UploadFileModel input) {
		ObjectMetadata metadata = new ObjectMetadata();
		PutObjectRequest request = new PutObjectRequest(bucketName, input.getFileName(), input.getInputStream(),
				metadata);
		s3.putObject(request);
		return "success";
	}

	public InputStream getFileFromS3(String fileName) {
		GetObjectRequest request = new GetObjectRequest(bucketName, fileName);
		S3Object object = s3.getObject(request);
		return object.getObjectContent();
	}

}
