package com.healthpay.graphql;

import com.healthpay.model.*;
import com.healthpay.repository.*;
import com.healthpay.service.FraudDetectionService;
import lombok.RequiredArgsConstructor;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.graphql.data.method.annotation.SchemaMapping;
import org.springframework.stereotype.Controller;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.math.BigDecimal;
import java.util.List;

@Controller
@RequiredArgsConstructor
public class ClaimController {
    private final FraudDetectionService fraudDetectionService;
    private final ClaimRepository claimRepository;
    private final PaymentErrorRepository paymentErrorRepository;
    private final FraudAlertRepository fraudAlertRepository;
    private final AbusePatternRepository abusePatternRepository;

    @QueryMapping
    public Mono<Claim> claim(@Argument String id) {
        return claimRepository.findById(id);
    }

    @QueryMapping
    public Mono<List<Claim>> claims() {
        return claimRepository.findAll().collectList();
    }

    @QueryMapping
    public Mono<List<PaymentError>> paymentErrors(@Argument String claimId) {
        return paymentErrorRepository.findByClaimId(claimId).collectList();
    }

    @QueryMapping
    public Mono<List<PaymentError>> allPaymentErrors() {
        return paymentErrorRepository.findAll().collectList();
    }

    @QueryMapping
    public Mono<List<FraudAlert>> fraudAlerts(@Argument String claimId) {
        return fraudAlertRepository.findByClaimId(claimId).collectList();
    }

    @QueryMapping
    public Mono<List<FraudAlert>> allFraudAlerts() {
        return fraudAlertRepository.findAll().collectList();
    }

    @QueryMapping
    public Mono<List<AbusePattern>> abusePatterns(@Argument String providerId) {
        return abusePatternRepository.findByProviderId(providerId).collectList();
    }

    @QueryMapping
    public Mono<List<AbusePattern>> allAbusePatterns() {
        return abusePatternRepository.findAll().collectList();
    }

    @MutationMapping
    public Mono<Claim> submitClaim(
            @Argument String patientId,
            @Argument String providerId,
            @Argument BigDecimal amount,
            @Argument List<String> diagnosisCodes,
            @Argument List<String> procedureCodes,
            @Argument String serviceDate) {
        return fraudDetectionService.submitClaim(
                patientId, providerId, amount, diagnosisCodes, procedureCodes, serviceDate
        );
    }

    @MutationMapping
    public Mono<Claim> processClaim(@Argument String claimId) {
        return fraudDetectionService.processClaim(claimId);
    }

    @MutationMapping
    public Mono<PaymentError> resolvePaymentError(@Argument String errorId) {
        return fraudDetectionService.resolvePaymentError(errorId);
    }

    @MutationMapping
    public Mono<FraudAlert> updateFraudAlertStatus(
            @Argument String alertId,
            @Argument AlertStatus status) {
        return fraudDetectionService.updateFraudAlertStatus(alertId, status);
    }

    @SchemaMapping(typeName = "Claim", field = "paymentErrors")
    public Mono<List<PaymentError>> paymentErrorsForClaim(Claim claim) {
        return paymentErrorRepository.findByClaimId(claim.getId()).collectList();
    }

    @SchemaMapping(typeName = "Claim", field = "fraudAlerts")
    public Mono<List<FraudAlert>> fraudAlertsForClaim(Claim claim) {
        return fraudAlertRepository.findByClaimId(claim.getId()).collectList();
    }
}
