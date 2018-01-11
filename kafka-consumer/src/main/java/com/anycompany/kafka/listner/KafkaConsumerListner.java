package com.anycompany.kafka.listner;

import static java.util.stream.StreamSupport.stream;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Spliterator;
import java.util.Spliterators.AbstractSpliterator;
import java.util.function.Consumer;
import java.util.stream.Stream;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class KafkaConsumerListner {

	@Autowired
	private RestTemplate template;
	
	@KafkaListener(topics = "filePath", group = "group-someFeed")
	public void kafkaListner(String filePath) {
		try {
			split(Paths.get(filePath), 100).forEach(this::sendRequest);
		} catch (IOException e) {
			e.printStackTrace();
		}

	}

	void sendRequest(List<String> each) {
		
		HttpEntity<List<String>> jsonDataRequest = new HttpEntity<>(each);
		ResponseEntity<String> response = template.postForEntity("http://somefeed/processSomeFeedData", jsonDataRequest,
				String.class);
		System.out.println("Response is " + response);
	}

	Stream<List<String>> split(Path path, int limit) throws IOException {
		// skip the remaining lines if its size < limit
		return split(Files.lines(path), limit, false);
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
