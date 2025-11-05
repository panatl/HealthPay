package com.healthpay.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "claims")
public class Claim {
    @Id
    private String claimId;
    private String patientId;
    private String providerId;
    private ClaimType claimType;
    private LocalDateTime serviceDate;
    private LocalDateTime submissionDate;
    private List<ServiceCode> services;
    private Double claimedAmount;
    private Double allowedAmount;
    private Double paidAmount;
    private ClaimStatus status;
    private List<String> diagnosisCodes;
}
