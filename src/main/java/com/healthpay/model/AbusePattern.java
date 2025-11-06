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
public class AbusePattern {
    private String id;
    private String providerId;
    private AbuseType abuseType;
    private String description;
    private Integer occurrenceCount;
    private LocalDateTime firstDetectedAt;
    private LocalDateTime lastDetectedAt;
    private List<String> affectedClaims;
}
