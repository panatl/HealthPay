package com.healthpay.graphql;

import com.healthpay.model.*;
import com.healthpay.repository.*;
import com.healthpay.service.FraudDetectionService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.concurrent.CompletableFuture;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ClaimDataFetcherTest {

    @Mock
    private FraudDetectionService fraudDetectionService;
    
    @Mock
    private ClaimRepository claimRepository;
    
    @Mock
    private PaymentErrorRepository paymentErrorRepository;
    
    @Mock
    private FraudAlertRepository fraudAlertRepository;
    
    @Mock
    private AbusePatternRepository abusePatternRepository;

    @InjectMocks
    private ClaimDataFetcher claimDataFetcher;

    @Test
    void testSubmitClaimMutation() throws Exception {
        // Arrange
        Claim claim = Claim.builder()
                .id("claim-123")
                .patientId("patient-123")
                .providerId("provider-456")
                .amount(new BigDecimal("5000.00"))
                .status(ClaimStatus.SUBMITTED)
                .submittedAt(LocalDateTime.now())
                .diagnosisCodes(List.of("D001", "D002"))
                .procedureCodes(List.of("P001"))
                .serviceDate("2024-01-15")
                .build();

        when(fraudDetectionService.submitClaim(
                any(), any(), any(), any(), any(), any()
        )).thenReturn(Mono.just(claim));

        // Act
        CompletableFuture<Claim> result = claimDataFetcher.submitClaim(
                "patient-123",
                "provider-456",
                new BigDecimal("5000.00"),
                List.of("D001", "D002"),
                List.of("P001"),
                "2024-01-15"
        );

        // Assert
        Claim resultClaim = result.get();
        assertEquals("patient-123", resultClaim.getPatientId());
        assertEquals("provider-456", resultClaim.getProviderId());
        assertEquals(new BigDecimal("5000.00"), resultClaim.getAmount());
    }
}
