package com.healthpay.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ClaimAnalysisResult {
    private String claimId;
    private Boolean isValid;
    private List<PaymentIntegrityIssue> issues;
    private Double totalEstimatedImpact;
    private Double riskScore;
    private LocalDateTime analysisTimestamp;
}
