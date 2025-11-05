package com.healthpay.repository;

import com.healthpay.model.Claim;
import org.springframework.stereotype.Repository;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class ClaimRepository {
    private final Map<String, Claim> claims = new ConcurrentHashMap<>();

    public Mono<Claim> save(Claim claim) {
        return Mono.fromCallable(() -> {
            claims.put(claim.getId(), claim);
            return claim;
        });
    }

    public Mono<Claim> findById(String id) {
        return Mono.justOrEmpty(claims.get(id));
    }

    public Flux<Claim> findAll() {
        return Flux.fromIterable(claims.values());
    }

    public Flux<Claim> findByProviderId(String providerId) {
        return Flux.fromIterable(claims.values())
                .filter(claim -> claim.getProviderId().equals(providerId));
    }

    public Flux<Claim> findByPatientId(String patientId) {
        return Flux.fromIterable(claims.values())
                .filter(claim -> claim.getPatientId().equals(patientId));
    }
}
