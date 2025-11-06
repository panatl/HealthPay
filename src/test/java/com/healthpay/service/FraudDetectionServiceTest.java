package com.healthpay.service;

import com.healthpay.model.*;
import com.healthpay.repository.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class FraudDetectionServiceTest {

    @Mock
    private ClaimRepository claimRepository;

    @Mock
    private PaymentErrorRepository paymentErrorRepository;

    @Mock
    private FraudAlertRepository fraudAlertRepository;

    @Mock
    private AbusePatternRepository abusePatternRepository;

    private FraudDetectionService fraudDetectionService;

    @BeforeEach
    void setUp() {
        fraudDetectionService = new FraudDetectionService(
                claimRepository,
                paymentErrorRepository,
                fraudAlertRepository,
                abusePatternRepository
        );
    }

    @Test
    void testSubmitClaim() {
        // Arrange
        String patientId = "patient-1";
        String providerId = "provider-1";
        BigDecimal amount = new BigDecimal("5000.00");
        List<String> diagnosisCodes = List.of("D001", "D002");
        List<String> procedureCodes = List.of("P001");
        String serviceDate = "2024-01-15";

        when(claimRepository.save(any(Claim.class)))
                .thenAnswer(invocation -> Mono.just(invocation.getArgument(0)));

        // Act & Assert
        StepVerifier.create(fraudDetectionService.submitClaim(
                        patientId, providerId, amount, diagnosisCodes, procedureCodes, serviceDate))
                .assertNext(claim -> {
                    assertNotNull(claim.getId());
                    assertEquals(patientId, claim.getPatientId());
                    assertEquals(providerId, claim.getProviderId());
                    assertEquals(amount, claim.getAmount());
                    assertEquals(ClaimStatus.SUBMITTED, claim.getStatus());
                    assertEquals(diagnosisCodes, claim.getDiagnosisCodes());
                    assertEquals(procedureCodes, claim.getProcedureCodes());
                    assertEquals(serviceDate, claim.getServiceDate());
                })
                .verifyComplete();
    }

    @Test
    void testDetectPaymentErrors_InvalidAmount() {
        // Arrange
        Claim claim = Claim.builder()
                .id("claim-1")
                .patientId("patient-1")
                .providerId("provider-1")
                .amount(new BigDecimal("-100.00"))
                .submittedAt(LocalDateTime.now())
                .status(ClaimStatus.SUBMITTED)
                .diagnosisCodes(List.of("D001"))
                .procedureCodes(List.of("P001"))
                .serviceDate("2024-01-15")
                .build();

        when(claimRepository.findByPatientId(any())).thenReturn(Flux.empty());
        when(paymentErrorRepository.save(any(PaymentError.class)))
                .thenAnswer(invocation -> Mono.just(invocation.getArgument(0)));

        // Act & Assert
        StepVerifier.create(fraudDetectionService.detectPaymentErrors(claim))
                .assertNext(error -> {
                    assertEquals(ErrorType.INVALID_AMOUNT, error.getErrorType());
                    assertEquals(ErrorSeverity.CRITICAL, error.getSeverity());
                    assertEquals("ERR-002", error.getErrorCode());
                    assertFalse(error.isResolved());
                })
                .verifyComplete();
    }

    @Test
    void testDetectPaymentErrors_MissingInformation() {
        // Arrange
        Claim claim = Claim.builder()
                .id("claim-1")
                .patientId("patient-1")
                .providerId("provider-1")
                .amount(new BigDecimal("5000.00"))
                .submittedAt(LocalDateTime.now())
                .status(ClaimStatus.SUBMITTED)
                .diagnosisCodes(List.of())
                .procedureCodes(List.of("P001"))
                .serviceDate("2024-01-15")
                .build();

        when(claimRepository.findByPatientId(any())).thenReturn(Flux.empty());
        when(paymentErrorRepository.save(any(PaymentError.class)))
                .thenAnswer(invocation -> Mono.just(invocation.getArgument(0)));

        // Act & Assert
        StepVerifier.create(fraudDetectionService.detectPaymentErrors(claim))
                .assertNext(error -> {
                    assertEquals(ErrorType.MISSING_INFORMATION, error.getErrorType());
                    assertEquals(ErrorSeverity.HIGH, error.getSeverity());
                    assertEquals("ERR-003", error.getErrorCode());
                })
                .verifyComplete();
    }

    @Test
    void testResolvePaymentError() {
        // Arrange
        PaymentError error = PaymentError.builder()
                .id("error-1")
                .claimId("claim-1")
                .errorType(ErrorType.INVALID_AMOUNT)
                .errorCode("ERR-002")
                .description("Test error")
                .severity(ErrorSeverity.HIGH)
                .detectedAt(LocalDateTime.now())
                .resolved(false)
                .build();

        when(paymentErrorRepository.findById("error-1")).thenReturn(Mono.just(error));
        when(paymentErrorRepository.save(any(PaymentError.class)))
                .thenAnswer(invocation -> Mono.just(invocation.getArgument(0)));

        // Act & Assert
        StepVerifier.create(fraudDetectionService.resolvePaymentError("error-1"))
                .assertNext(resolvedError -> {
                    assertTrue(resolvedError.isResolved());
                })
                .verifyComplete();
    }

    @Test
    void testUpdateFraudAlertStatus() {
        // Arrange
        FraudAlert alert = FraudAlert.builder()
                .id("alert-1")
                .claimId("claim-1")
                .fraudType(FraudType.DUPLICATE_BILLING)
                .description("Test alert")
                .riskScore(new BigDecimal("75"))
                .detectedAt(LocalDateTime.now())
                .status(AlertStatus.OPEN)
                .indicators(List.of("indicator-1"))
                .build();

        when(fraudAlertRepository.findById("alert-1")).thenReturn(Mono.just(alert));
        when(fraudAlertRepository.save(any(FraudAlert.class)))
                .thenAnswer(invocation -> Mono.just(invocation.getArgument(0)));

        // Act & Assert
        StepVerifier.create(fraudDetectionService.updateFraudAlertStatus("alert-1", AlertStatus.CONFIRMED))
                .assertNext(updatedAlert -> {
                    assertEquals(AlertStatus.CONFIRMED, updatedAlert.getStatus());
                })
                .verifyComplete();
    }
}
