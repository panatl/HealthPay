package com.healthpay.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PaymentError {
    private String id;
    private String claimId;
    private ErrorType errorType;
    private String errorCode;
    private String description;
    private ErrorSeverity severity;
    private LocalDateTime detectedAt;
    private boolean resolved;
}
