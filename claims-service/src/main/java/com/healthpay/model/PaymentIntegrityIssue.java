package com.healthpay.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PaymentIntegrityIssue {
    private String issueType;
    private Severity severity;
    private String description;
    private Double estimatedImpact;
    private String recommendation;
}
