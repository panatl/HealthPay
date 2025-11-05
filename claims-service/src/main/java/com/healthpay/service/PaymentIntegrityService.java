package com.healthpay.service;

import com.healthpay.model.*;
import com.healthpay.repository.ClaimRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class PaymentIntegrityService {

    private final ClaimRepository claimRepository;

    public Mono<ClaimAnalysisResult> analyzeClaim(Claim claim) {
        return Mono.fromCallable(() -> {
            List<PaymentIntegrityIssue> issues = new ArrayList<>();

            // Check for overpayment
            if (claim.getPaidAmount() != null && claim.getAllowedAmount() != null) {
                if (claim.getPaidAmount() > claim.getAllowedAmount()) {
                    double overpayment = claim.getPaidAmount() - claim.getAllowedAmount();
                    issues.add(PaymentIntegrityIssue.builder()
                            .issueType("overpayment")
                            .severity(Severity.HIGH)
                            .description(String.format("Claim paid $%.2f exceeds allowed amount $%.2f", 
                                    claim.getPaidAmount(), claim.getAllowedAmount()))
                            .estimatedImpact(overpayment)
                            .recommendation("Recover overpaid amount from provider")
                            .build());
                }
            }

            // Check for underpayment
            if (claim.getPaidAmount() != null && claim.getAllowedAmount() != null) {
                if (claim.getPaidAmount() < claim.getAllowedAmount() && 
                    claim.getStatus() == ClaimStatus.APPROVED) {
                    double underpayment = claim.getAllowedAmount() - claim.getPaidAmount();
                    if (underpayment > 0.01) {
                        issues.add(PaymentIntegrityIssue.builder()
                                .issueType("underpayment")
                                .severity(Severity.MEDIUM)
                                .description(String.format("Claim paid $%.2f is less than allowed amount $%.2f", 
                                        claim.getPaidAmount(), claim.getAllowedAmount()))
                                .estimatedImpact(-underpayment)
                                .recommendation("Issue supplemental payment to provider")
                                .build());
                    }
                }
            }

            // Check for pricing errors
            double calculatedAmount = claim.getServices().stream()
                    .mapToDouble(s -> s.getUnits() * s.getUnitPrice())
                    .sum();
            if (Math.abs(calculatedAmount - claim.getClaimedAmount()) > 0.01) {
                issues.add(PaymentIntegrityIssue.builder()
                        .issueType("pricing_error")
                        .severity(Severity.MEDIUM)
                        .description(String.format("Claimed amount $%.2f does not match calculated amount $%.2f", 
                                claim.getClaimedAmount(), calculatedAmount))
                        .estimatedImpact(Math.abs(calculatedAmount - claim.getClaimedAmount()))
                        .recommendation("Review service pricing and recalculate")
                        .build());
            }

            // Check for duplicate services
            Map<String, Long> serviceCounts = claim.getServices().stream()
                    .collect(Collectors.groupingBy(ServiceCode::getCode, Collectors.counting()));
            serviceCounts.forEach((code, count) -> {
                if (count > 1) {
                    issues.add(PaymentIntegrityIssue.builder()
                            .issueType("duplicate_service")
                            .severity(Severity.HIGH)
                            .description(String.format("Duplicate service code found: %s", code))
                            .estimatedImpact(0.0)
                            .recommendation("Review and remove duplicate services")
                            .build());
                }
            });

            // Check for excessive units
            claim.getServices().forEach(service -> {
                if (service.getUnits() > 20) {
                    issues.add(PaymentIntegrityIssue.builder()
                            .issueType("excessive_units")
                            .severity(Severity.MEDIUM)
                            .description(String.format("Service %s has %d units, which seems excessive", 
                                    service.getCode(), service.getUnits()))
                            .estimatedImpact(0.0)
                            .recommendation("Review medical necessity for high unit count")
                            .build());
                }
            });

            // Check for late filing
            if (claim.getSubmissionDate() != null) {
                long daysToSubmit = ChronoUnit.DAYS.between(claim.getServiceDate(), claim.getSubmissionDate());
                if (daysToSubmit > 90) {
                    issues.add(PaymentIntegrityIssue.builder()
                            .issueType("late_filing")
                            .severity(Severity.LOW)
                            .description(String.format("Claim submitted %d days after service date", daysToSubmit))
                            .estimatedImpact(0.0)
                            .recommendation("Consider timely filing rules in adjudication")
                            .build());
                }
            }

            // Check for missing diagnosis
            if (claim.getDiagnosisCodes() == null || claim.getDiagnosisCodes().isEmpty()) {
                issues.add(PaymentIntegrityIssue.builder()
                        .issueType("missing_diagnosis")
                        .severity(Severity.MEDIUM)
                        .description("Claim has no diagnosis codes")
                        .estimatedImpact(0.0)
                        .recommendation("Request diagnosis codes from provider")
                        .build());
            }

            // Calculate risk score
            double riskScore = calculateRiskScore(issues, claim);
            
            // Calculate total impact
            double totalImpact = issues.stream()
                    .mapToDouble(PaymentIntegrityIssue::getEstimatedImpact)
                    .sum();

            return ClaimAnalysisResult.builder()
                    .claimId(claim.getClaimId())
                    .isValid(issues.stream().noneMatch(i -> 
                            i.getSeverity() == Severity.HIGH || i.getSeverity() == Severity.CRITICAL))
                    .issues(issues)
                    .totalEstimatedImpact(totalImpact)
                    .riskScore(riskScore)
                    .analysisTimestamp(LocalDateTime.now())
                    .build();
        });
    }

    private double calculateRiskScore(List<PaymentIntegrityIssue> issues, Claim claim) {
        double score = 0.0;
        
        for (PaymentIntegrityIssue issue : issues) {
            switch (issue.getSeverity()) {
                case CRITICAL -> score += 40;
                case HIGH -> score += 25;
                case MEDIUM -> score += 15;
                case LOW -> score += 5;
            }
        }
        
        // Add factors based on claim amount
        if (claim.getClaimedAmount() > 10000) {
            score += 10;
        } else if (claim.getClaimedAmount() > 5000) {
            score += 5;
        }
        
        return Math.min(score, 100.0);
    }

    public Flux<ClaimAnalysisResult> batchAnalyzeClaims(List<Claim> claims) {
        return Flux.fromIterable(claims)
                .flatMap(this::analyzeClaim);
    }

    public Mono<Claim> saveClaim(Claim claim) {
        return claimRepository.save(claim);
    }

    public Mono<Claim> getClaim(String claimId) {
        return claimRepository.findById(claimId);
    }
}
