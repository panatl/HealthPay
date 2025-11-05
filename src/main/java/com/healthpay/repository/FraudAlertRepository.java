package com.healthpay.repository;

import com.healthpay.model.FraudAlert;
import org.springframework.stereotype.Repository;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class FraudAlertRepository {
    private final Map<String, FraudAlert> alerts = new ConcurrentHashMap<>();

    public Mono<FraudAlert> save(FraudAlert alert) {
        return Mono.fromCallable(() -> {
            alerts.put(alert.getId(), alert);
            return alert;
        });
    }

    public Mono<FraudAlert> findById(String id) {
        return Mono.justOrEmpty(alerts.get(id));
    }

    public Flux<FraudAlert> findAll() {
        return Flux.fromIterable(alerts.values());
    }

    public Flux<FraudAlert> findByClaimId(String claimId) {
        return Flux.fromIterable(alerts.values())
                .filter(alert -> alert.getClaimId().equals(claimId));
    }
}
