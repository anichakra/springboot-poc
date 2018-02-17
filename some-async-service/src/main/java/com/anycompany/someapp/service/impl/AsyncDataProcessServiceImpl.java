package com.anycompany.someapp.service.impl;

import static java.util.stream.StreamSupport.stream;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.Spliterator;
import java.util.Spliterators.AbstractSpliterator;
import java.util.function.Consumer;
import java.util.stream.Stream;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.anycompany.someapp.s3.S3Actions;

@Service
public class AsyncDataProcessServiceImpl {

	@Autowired
	private S3Actions action;

	@Autowired
	RestTemplate template;

	@Async("asyncExecutor")
	public void startProcessing(String fileName) {
		try {
			System.out.println("This is Thread "+ Thread.currentThread().getName());
			split(action.getFileFromS3(fileName), 100).forEach(this::sendRequest);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	void sendRequest(List<String> chunk) {
		try {
			HttpEntity<List<String>> jsonDataRequest = new HttpEntity<>(chunk);
			template.postForEntity("http://some-app-service/processRawSomeFeedData", jsonDataRequest, String.class);
			System.out.println("Data processed size " + chunk.size());
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	Stream<List<String>> split(InputStream input, int limit) throws IOException {
		// skip the remaining lines if its size < limit
		return split(new BufferedReader(new InputStreamReader(input)).lines().skip(1), limit, false);
	}

	<T> Stream<List<T>> split(Stream<T> source, int limit, boolean skipRemainingElements) {

		// variables just for printing purpose
		Spliterator<T> it = source.spliterator();
		long size = it.estimateSize();
		int c = it.characteristics();// characteristics

		return stream(new AbstractSpliterator<List<T>>(size, c) {
			private int thresholds = skipRemainingElements ? limit : 1;

			@Override
			public boolean tryAdvance(Consumer<? super List<T>> action) {
				List<T> each = new ArrayList<>(limit);

				while (each.size() < limit && it.tryAdvance(each::add))
					;

				if (each.size() < thresholds)
					return false;

				action.accept(each);
				return true;
			}

		}, false).onClose(source::close);
	}

}
