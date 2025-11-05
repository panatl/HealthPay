package com.healthpay.resolver;

import com.healthpay.model.Claim;
import com.healthpay.model.ClaimAnalysisResult;
import com.healthpay.service.PaymentIntegrityService;
import com.netflix.graphql.dgs.DgsComponent;
import com.netflix.graphql.dgs.DgsQuery;
import com.netflix.graphql.dgs.DgsMutation;
import com.netflix.graphql.dgs.InputArgument;
import lombok.RequiredArgsConstructor;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.List;

@DgsComponent
@RequiredArgsConstructor
public class ClaimResolver {

    private final PaymentIntegrityService paymentIntegrityService;

    @DgsQuery
    public Mono<ClaimAnalysisResult> analyzeClaim(@InputArgument("input") Claim input) {
        return paymentIntegrityService.analyzeClaim(input);
    }

    @DgsQuery
    public Flux<ClaimAnalysisResult> batchAnalyzeClaims(@InputArgument("inputs") List<Claim> inputs) {
        return paymentIntegrityService.batchAnalyzeClaims(inputs);
    }

    @DgsQuery
    public Mono<Claim> getClaim(@InputArgument("claimId") String claimId) {
        return paymentIntegrityService.getClaim(claimId);
    }

    @DgsMutation
    public Mono<Claim> submitClaim(@InputArgument("input") Claim input) {
        return paymentIntegrityService.saveClaim(input);
    }
}
