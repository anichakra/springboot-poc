package com.jahnelgroup.queue.hazelcast.reliableQueue;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.core.IQueue;
import com.hazelcast.core.ItemEvent;
import com.hazelcast.core.ItemListener;

@Component
public class ReliableMessageSubscriber {

    private Logger logger = LoggerFactory.getLogger(ReliableMessageSubscriber.class);

    private IQueue<ReliableMessage> reliableQueue;
    
    public static String QUEUE_NAME = "reliableQueue";

    public ReliableMessageSubscriber(HazelcastInstance hazelcastInstance) {
        this.reliableQueue = hazelcastInstance.getQueue(QUEUE_NAME);
        this.reliableQueue.addItemListener(
                new ItemListener<ReliableMessage>() {
                    @Override
                    public void itemAdded(ItemEvent<ReliableMessage> item) {
                        logger.info("ReliableQueue itemAdded: {}", item);
                    }

                    @Override
                    public void itemRemoved(ItemEvent<ReliableMessage> item) {
                        logger.info("ReliableQueue itemRemoved: {}", item);
                    }
                }, true);
        logger.info("Starting ReliableMessageSubscriber");
    }

    @Scheduled(fixedRate = 5000L)
    public void publish() {
        List<ReliableMessage> receivedMessages = new ArrayList<ReliableMessage>();
        reliableQueue.drainTo(receivedMessages);

        logger.info("Drained {} messages: {}",
                receivedMessages.size(),
                receivedMessages.stream()
                        .map(ReliableMessage::getMessage)
                        .collect(Collectors.joining(",")));
    }

}
