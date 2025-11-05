package com.healthpay.repository;

import com.healthpay.model.PaymentError;
import org.springframework.stereotype.Repository;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class PaymentErrorRepository {
    private final Map<String, PaymentError> errors = new ConcurrentHashMap<>();

    public Mono<PaymentError> save(PaymentError error) {
        return Mono.fromCallable(() -> {
            errors.put(error.getId(), error);
            return error;
        });
    }

    public Mono<PaymentError> findById(String id) {
        return Mono.justOrEmpty(errors.get(id));
    }

    public Flux<PaymentError> findAll() {
        return Flux.fromIterable(errors.values());
    }

    public Flux<PaymentError> findByClaimId(String claimId) {
        return Flux.fromIterable(errors.values())
                .filter(error -> error.getClaimId().equals(claimId));
    }
}
