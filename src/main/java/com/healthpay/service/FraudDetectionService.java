package com.healthpay.service;

import com.healthpay.model.*;
import com.healthpay.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class FraudDetectionService {
    private final ClaimRepository claimRepository;
    private final PaymentErrorRepository paymentErrorRepository;
    private final FraudAlertRepository fraudAlertRepository;
    private final AbusePatternRepository abusePatternRepository;

    private static final BigDecimal HIGH_AMOUNT_THRESHOLD = new BigDecimal("10000.00");
    private static final int DUPLICATE_CHECK_HOURS = 24;
    private static final int FREQUENCY_THRESHOLD = 5;

    public Mono<Claim> submitClaim(String patientId, String providerId, BigDecimal amount,
                                    List<String> diagnosisCodes, List<String> procedureCodes,
                                    String serviceDate) {
        Claim claim = Claim.builder()
                .id(UUID.randomUUID().toString())
                .patientId(patientId)
                .providerId(providerId)
                .amount(amount)
                .submittedAt(LocalDateTime.now())
                .status(ClaimStatus.SUBMITTED)
                .diagnosisCodes(diagnosisCodes)
                .procedureCodes(procedureCodes)
                .serviceDate(serviceDate)
                .build();

        return claimRepository.save(claim);
    }

    public Mono<Claim> processClaim(String claimId) {
        return claimRepository.findById(claimId)
                .flatMap(claim -> {
                    claim.setStatus(ClaimStatus.UNDER_REVIEW);
                    
                    return detectPaymentErrors(claim)
                            .collectList()
                            .flatMap(errors -> detectFraudAlerts(claim, errors)
                                    .collectList()
                                    .flatMap(alerts -> {
                                        if (!alerts.isEmpty()) {
                                            claim.setStatus(ClaimStatus.FLAGGED_FOR_FRAUD);
                                        } else if (!errors.isEmpty() && errors.stream()
                                                .anyMatch(e -> e.getSeverity() == ErrorSeverity.CRITICAL)) {
                                            claim.setStatus(ClaimStatus.REQUIRES_MANUAL_REVIEW);
                                        } else if (!errors.isEmpty()) {
                                            claim.setStatus(ClaimStatus.REQUIRES_MANUAL_REVIEW);
                                        } else {
                                            claim.setStatus(ClaimStatus.APPROVED);
                                        }
                                        
                                        return updateAbusePatterns(claim)
                                                .then(claimRepository.save(claim));
                                    }));
                });
    }

    public Flux<PaymentError> detectPaymentErrors(Claim claim) {
        List<Mono<PaymentError>> errorDetectors = new ArrayList<>();

        // Check for duplicate claims
        errorDetectors.add(checkDuplicateClaim(claim));

        // Check for invalid amounts
        errorDetectors.add(checkInvalidAmount(claim));

        // Check for missing information
        errorDetectors.add(checkMissingInformation(claim));

        return Flux.merge(errorDetectors)
                .filter(error -> error != null)
                .flatMap(paymentErrorRepository::save);
    }

    private Mono<PaymentError> checkDuplicateClaim(Claim claim) {
        return claimRepository.findByPatientId(claim.getPatientId())
                .filter(existingClaim -> !existingClaim.getId().equals(claim.getId()))
                .filter(existingClaim -> {
                    long hoursBetween = ChronoUnit.HOURS.between(
                            existingClaim.getSubmittedAt(), claim.getSubmittedAt());
                    return Math.abs(hoursBetween) < DUPLICATE_CHECK_HOURS &&
                            existingClaim.getAmount().equals(claim.getAmount()) &&
                            existingClaim.getServiceDate().equals(claim.getServiceDate());
                })
                .next()
                .map(duplicate -> PaymentError.builder()
                        .id(UUID.randomUUID().toString())
                        .claimId(claim.getId())
                        .errorType(ErrorType.DUPLICATE_CLAIM)
                        .errorCode("ERR-001")
                        .description("Duplicate claim detected for same service within " + DUPLICATE_CHECK_HOURS + " hours")
                        .severity(ErrorSeverity.HIGH)
                        .detectedAt(LocalDateTime.now())
                        .resolved(false)
                        .build());
    }

    private Mono<PaymentError> checkInvalidAmount(Claim claim) {
        if (claim.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            return Mono.just(PaymentError.builder()
                    .id(UUID.randomUUID().toString())
                    .claimId(claim.getId())
                    .errorType(ErrorType.INVALID_AMOUNT)
                    .errorCode("ERR-002")
                    .description("Claim amount must be greater than zero")
                    .severity(ErrorSeverity.CRITICAL)
                    .detectedAt(LocalDateTime.now())
                    .resolved(false)
                    .build());
        }
        return Mono.empty();
    }

    private Mono<PaymentError> checkMissingInformation(Claim claim) {
        if (claim.getDiagnosisCodes() == null || claim.getDiagnosisCodes().isEmpty()) {
            return Mono.just(PaymentError.builder()
                    .id(UUID.randomUUID().toString())
                    .claimId(claim.getId())
                    .errorType(ErrorType.MISSING_INFORMATION)
                    .errorCode("ERR-003")
                    .description("Missing diagnosis codes")
                    .severity(ErrorSeverity.HIGH)
                    .detectedAt(LocalDateTime.now())
                    .resolved(false)
                    .build());
        }
        return Mono.empty();
    }

    public Flux<FraudAlert> detectFraudAlerts(Claim claim, List<PaymentError> errors) {
        List<Mono<FraudAlert>> alertDetectors = new ArrayList<>();

        // Check for excessive amount
        alertDetectors.add(checkExcessiveAmount(claim));

        // Check for duplicate billing fraud
        alertDetectors.add(checkDuplicateBillingFraud(claim));

        // Check for excessive service frequency
        alertDetectors.add(checkExcessiveServiceFrequency(claim));

        return Flux.merge(alertDetectors)
                .filter(alert -> alert != null)
                .flatMap(fraudAlertRepository::save);
    }

    private Mono<FraudAlert> checkExcessiveAmount(Claim claim) {
        if (claim.getAmount().compareTo(HIGH_AMOUNT_THRESHOLD) > 0) {
            BigDecimal riskScore = claim.getAmount()
                    .divide(HIGH_AMOUNT_THRESHOLD, 2, BigDecimal.ROUND_HALF_UP)
                    .multiply(new BigDecimal("50"));
            
            return Mono.just(FraudAlert.builder()
                    .id(UUID.randomUUID().toString())
                    .claimId(claim.getId())
                    .fraudType(FraudType.EXCESSIVE_SERVICES)
                    .description("Claim amount exceeds typical threshold")
                    .riskScore(riskScore.min(new BigDecimal("100")))
                    .detectedAt(LocalDateTime.now())
                    .status(AlertStatus.OPEN)
                    .indicators(List.of("High claim amount", "Amount: " + claim.getAmount()))
                    .build());
        }
        return Mono.empty();
    }

    private Mono<FraudAlert> checkDuplicateBillingFraud(Claim claim) {
        return claimRepository.findByPatientId(claim.getPatientId())
                .filter(existingClaim -> !existingClaim.getId().equals(claim.getId()))
                .filter(existingClaim -> {
                    long hoursBetween = ChronoUnit.HOURS.between(
                            existingClaim.getSubmittedAt(), claim.getSubmittedAt());
                    return Math.abs(hoursBetween) < DUPLICATE_CHECK_HOURS &&
                            existingClaim.getAmount().equals(claim.getAmount()) &&
                            existingClaim.getServiceDate().equals(claim.getServiceDate());
                })
                .collectList()
                .flatMap(duplicates -> {
                    if (!duplicates.isEmpty()) {
                        return Mono.just(FraudAlert.builder()
                                .id(UUID.randomUUID().toString())
                                .claimId(claim.getId())
                                .fraudType(FraudType.DUPLICATE_BILLING)
                                .description("Multiple identical claims detected")
                                .riskScore(new BigDecimal("85"))
                                .detectedAt(LocalDateTime.now())
                                .status(AlertStatus.OPEN)
                                .indicators(List.of("Duplicate claims found", "Count: " + duplicates.size()))
                                .build());
                    }
                    return Mono.empty();
                });
    }

    private Mono<FraudAlert> checkExcessiveServiceFrequency(Claim claim) {
        return claimRepository.findByProviderId(claim.getProviderId())
                .filter(c -> {
                    long daysBetween = ChronoUnit.DAYS.between(
                            c.getSubmittedAt(), LocalDateTime.now());
                    return daysBetween <= 7;
                })
                .collectList()
                .flatMap(recentClaims -> {
                    if (recentClaims.size() >= FREQUENCY_THRESHOLD) {
                        return Mono.just(FraudAlert.builder()
                                .id(UUID.randomUUID().toString())
                                .claimId(claim.getId())
                                .fraudType(FraudType.EXCESSIVE_SERVICES)
                                .description("Provider has submitted excessive claims in short period")
                                .riskScore(new BigDecimal("70"))
                                .detectedAt(LocalDateTime.now())
                                .status(AlertStatus.OPEN)
                                .indicators(List.of("High frequency", "Claims in 7 days: " + recentClaims.size()))
                                .build());
                    }
                    return Mono.empty();
                });
    }

    private Mono<Void> updateAbusePatterns(Claim claim) {
        return claimRepository.findByProviderId(claim.getProviderId())
                .filter(c -> {
                    long daysBetween = ChronoUnit.DAYS.between(
                            c.getSubmittedAt(), LocalDateTime.now());
                    return daysBetween <= 30;
                })
                .collectList()
                .flatMap(recentClaims -> {
                    if (recentClaims.size() >= 10) {
                        return abusePatternRepository.findByProviderId(claim.getProviderId())
                                .next()
                                .switchIfEmpty(Mono.defer(() -> {
                                    AbusePattern pattern = AbusePattern.builder()
                                            .id(UUID.randomUUID().toString())
                                            .providerId(claim.getProviderId())
                                            .abuseType(AbuseType.OVER_UTILIZATION)
                                            .description("Provider shows pattern of over-utilization")
                                            .occurrenceCount(1)
                                            .firstDetectedAt(LocalDateTime.now())
                                            .lastDetectedAt(LocalDateTime.now())
                                            .affectedClaims(List.of(claim.getId()))
                                            .build();
                                    return Mono.just(pattern);
                                }))
                                .flatMap(pattern -> {
                                    pattern.setOccurrenceCount(pattern.getOccurrenceCount() + 1);
                                    pattern.setLastDetectedAt(LocalDateTime.now());
                                    List<String> claims = new ArrayList<>(pattern.getAffectedClaims());
                                    claims.add(claim.getId());
                                    pattern.setAffectedClaims(claims);
                                    return abusePatternRepository.save(pattern);
                                })
                                .then();
                    }
                    return Mono.empty();
                });
    }

    public Mono<PaymentError> resolvePaymentError(String errorId) {
        return paymentErrorRepository.findById(errorId)
                .flatMap(error -> {
                    error.setResolved(true);
                    return paymentErrorRepository.save(error);
                });
    }

    public Mono<FraudAlert> updateFraudAlertStatus(String alertId, AlertStatus status) {
        return fraudAlertRepository.findById(alertId)
                .flatMap(alert -> {
                    alert.setStatus(status);
                    return fraudAlertRepository.save(alert);
                });
    }
}
