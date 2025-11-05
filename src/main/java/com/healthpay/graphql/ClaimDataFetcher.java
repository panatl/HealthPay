package com.healthpay.graphql;

import com.healthpay.model.*;
import com.healthpay.repository.*;
import com.healthpay.service.FraudDetectionService;
import com.netflix.graphql.dgs.*;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.RequestHeader;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.math.BigDecimal;
import java.util.List;
import java.util.concurrent.CompletableFuture;

@DgsComponent
@RequiredArgsConstructor
public class ClaimDataFetcher {
    private final FraudDetectionService fraudDetectionService;
    private final ClaimRepository claimRepository;
    private final PaymentErrorRepository paymentErrorRepository;
    private final FraudAlertRepository fraudAlertRepository;
    private final AbusePatternRepository abusePatternRepository;

    @DgsQuery
    public CompletableFuture<Claim> claim(@InputArgument String id) {
        return claimRepository.findById(id).toFuture();
    }

    @DgsQuery
    public CompletableFuture<List<Claim>> claims() {
        return claimRepository.findAll().collectList().toFuture();
    }

    @DgsQuery
    public CompletableFuture<List<PaymentError>> paymentErrors(@InputArgument String claimId) {
        return paymentErrorRepository.findByClaimId(claimId).collectList().toFuture();
    }

    @DgsQuery
    public CompletableFuture<List<PaymentError>> allPaymentErrors() {
        return paymentErrorRepository.findAll().collectList().toFuture();
    }

    @DgsQuery
    public CompletableFuture<List<FraudAlert>> fraudAlerts(@InputArgument String claimId) {
        return fraudAlertRepository.findByClaimId(claimId).collectList().toFuture();
    }

    @DgsQuery
    public CompletableFuture<List<FraudAlert>> allFraudAlerts() {
        return fraudAlertRepository.findAll().collectList().toFuture();
    }

    @DgsQuery
    public CompletableFuture<List<AbusePattern>> abusePatterns(@InputArgument String providerId) {
        return abusePatternRepository.findByProviderId(providerId).collectList().toFuture();
    }

    @DgsQuery
    public CompletableFuture<List<AbusePattern>> allAbusePatterns() {
        return abusePatternRepository.findAll().collectList().toFuture();
    }

    @DgsMutation
    public CompletableFuture<Claim> submitClaim(
            @InputArgument String patientId,
            @InputArgument String providerId,
            @InputArgument BigDecimal amount,
            @InputArgument List<String> diagnosisCodes,
            @InputArgument List<String> procedureCodes,
            @InputArgument String serviceDate) {
        return fraudDetectionService.submitClaim(
                patientId, providerId, amount, diagnosisCodes, procedureCodes, serviceDate
        ).toFuture();
    }

    @DgsMutation
    public CompletableFuture<Claim> processClaim(@InputArgument String claimId) {
        return fraudDetectionService.processClaim(claimId).toFuture();
    }

    @DgsMutation
    public CompletableFuture<PaymentError> resolvePaymentError(@InputArgument String errorId) {
        return fraudDetectionService.resolvePaymentError(errorId).toFuture();
    }

    @DgsMutation
    public CompletableFuture<FraudAlert> updateFraudAlertStatus(
            @InputArgument String alertId,
            @InputArgument AlertStatus status) {
        return fraudDetectionService.updateFraudAlertStatus(alertId, status).toFuture();
    }

    @DgsData(parentType = "Claim", field = "paymentErrors")
    public CompletableFuture<List<PaymentError>> paymentErrorsForClaim(DgsDataFetchingEnvironment dfe) {
        Claim claim = dfe.getSource();
        return paymentErrorRepository.findByClaimId(claim.getId()).collectList().toFuture();
    }

    @DgsData(parentType = "Claim", field = "fraudAlerts")
    public CompletableFuture<List<FraudAlert>> fraudAlertsForClaim(DgsDataFetchingEnvironment dfe) {
        Claim claim = dfe.getSource();
        return fraudAlertRepository.findByClaimId(claim.getId()).collectList().toFuture();
    }

    @DgsEntityFetcher(name = "Claim")
    public CompletableFuture<Claim> claimEntityFetcher(@InputArgument("id") String id) {
        return claimRepository.findById(id).toFuture();
    }

    @DgsEntityFetcher(name = "PaymentError")
    public CompletableFuture<PaymentError> paymentErrorEntityFetcher(@InputArgument("id") String id) {
        return paymentErrorRepository.findById(id).toFuture();
    }

    @DgsEntityFetcher(name = "FraudAlert")
    public CompletableFuture<FraudAlert> fraudAlertEntityFetcher(@InputArgument("id") String id) {
        return fraudAlertRepository.findById(id).toFuture();
    }

    @DgsEntityFetcher(name = "AbusePattern")
    public CompletableFuture<AbusePattern> abusePatternEntityFetcher(@InputArgument("id") String id) {
        return abusePatternRepository.findById(id).toFuture();
    }
}
