package com.healthpay.repository;

import com.healthpay.model.AbusePattern;
import org.springframework.stereotype.Repository;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class AbusePatternRepository {
    private final Map<String, AbusePattern> patterns = new ConcurrentHashMap<>();

    public Mono<AbusePattern> save(AbusePattern pattern) {
        return Mono.fromCallable(() -> {
            patterns.put(pattern.getId(), pattern);
            return pattern;
        });
    }

    public Mono<AbusePattern> findById(String id) {
        return Mono.justOrEmpty(patterns.get(id));
    }

    public Flux<AbusePattern> findAll() {
        return Flux.fromIterable(patterns.values());
    }

    public Flux<AbusePattern> findByProviderId(String providerId) {
        return Flux.fromIterable(patterns.values())
                .filter(pattern -> pattern.getProviderId().equals(providerId));
    }
}
