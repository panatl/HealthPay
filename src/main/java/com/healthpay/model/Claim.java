package com.healthpay.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Claim {
    private String id;
    private String patientId;
    private String providerId;
    private BigDecimal amount;
    private LocalDateTime submittedAt;
    private ClaimStatus status;
    private List<String> diagnosisCodes;
    private List<String> procedureCodes;
    private String serviceDate;
}
