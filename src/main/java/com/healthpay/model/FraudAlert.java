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
public class FraudAlert {
    private String id;
    private String claimId;
    private FraudType fraudType;
    private String description;
    private BigDecimal riskScore;
    private LocalDateTime detectedAt;
    private AlertStatus status;
    private List<String> indicators;
}
