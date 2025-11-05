# HealthPay - Healthcare Claims Fraud Detection System

A Spring Boot Reactive Microservices application for detecting payment errors, fraud, and abuse in healthcare claims processing, exposed through GraphQL Federation Spec 2.0.

## Features

- **Payment Error Detection**: Automatically detects various payment errors including:
  - Duplicate claims
  - Invalid amounts
  - Missing information
  - Provider authorization issues
  - Patient eligibility problems

- **Fraud Detection**: Identifies fraudulent activities such as:
  - Phantom billing
  - Upcoding
  - Unbundling
  - Duplicate billing
  - Excessive services
  - Identity theft

- **Abuse Pattern Detection**: Monitors and identifies patterns of abuse including:
  - Over-utilization of services
  - Pattern of errors
  - Unnecessary services
  - Inappropriate coding
  - Excessive charges

- **GraphQL Federation 2.0**: Implements Apollo Federation v2.0 specification for distributed GraphQL architecture

- **Reactive Programming**: Built with Spring WebFlux and Project Reactor for non-blocking, reactive processing

## Technology Stack

- **Spring Boot 3.2.0**: Core framework
- **Spring WebFlux**: Reactive web framework
- **Netflix DGS 8.1.1**: GraphQL framework with Federation support
- **Apollo Federation 3.0.0**: GraphQL Federation implementation
- **Project Reactor**: Reactive programming library
- **Java 17**: Programming language
- **Gradle 8.4**: Build tool

## Getting Started

### Prerequisites

- Java 17 or higher
- Gradle 8.4 or higher (or use included wrapper)

### Building the Application

```bash
./gradlew build
```

### Running the Application

```bash
./gradlew bootRun
```

The application will start on port 8080.

### Accessing GraphQL Playground

Once the application is running, access the GraphiQL interface at:

```
http://localhost:8080/graphiql
```

## GraphQL API

### Queries

#### Get a claim by ID
```graphql
query {
  claim(id: "claim-123") {
    id
    patientId
    providerId
    amount
    status
    diagnosisCodes
    procedureCodes
    serviceDate
    paymentErrors {
      id
      errorType
      severity
      description
    }
    fraudAlerts {
      id
      fraudType
      riskScore
      status
    }
  }
}
```

#### Get all payment errors
```graphql
query {
  allPaymentErrors {
    id
    claimId
    errorType
    errorCode
    description
    severity
    detectedAt
    resolved
  }
}
```

#### Get fraud alerts for a claim
```graphql
query {
  fraudAlerts(claimId: "claim-123") {
    id
    fraudType
    description
    riskScore
    status
    indicators
  }
}
```

#### Get abuse patterns for a provider
```graphql
query {
  abusePatterns(providerId: "provider-456") {
    id
    abuseType
    description
    occurrenceCount
    firstDetectedAt
    lastDetectedAt
    affectedClaims
  }
}
```

### Mutations

#### Submit a new claim
```graphql
mutation {
  submitClaim(
    patientId: "patient-123"
    providerId: "provider-456"
    amount: "5000.00"
    diagnosisCodes: ["D001", "D002"]
    procedureCodes: ["P001"]
    serviceDate: "2024-01-15"
  ) {
    id
    status
    submittedAt
  }
}
```

#### Process a claim for fraud detection
```graphql
mutation {
  processClaim(claimId: "claim-123") {
    id
    status
    paymentErrors {
      errorType
      severity
    }
    fraudAlerts {
      fraudType
      riskScore
    }
  }
}
```

#### Resolve a payment error
```graphql
mutation {
  resolvePaymentError(errorId: "error-123") {
    id
    resolved
  }
}
```

#### Update fraud alert status
```graphql
mutation {
  updateFraudAlertStatus(alertId: "alert-123", status: CONFIRMED) {
    id
    status
  }
}
```

## Fraud Detection Logic

The system implements multiple fraud detection algorithms:

1. **Excessive Amount Check**: Flags claims exceeding $10,000
2. **Duplicate Billing Detection**: Identifies identical claims within 24 hours
3. **Service Frequency Analysis**: Monitors providers submitting 5+ claims in 7 days
4. **Abuse Pattern Tracking**: Tracks providers with 10+ claims in 30 days

## Configuration

Application settings can be configured in `src/main/resources/application.yml`:

```yaml
fraud:
  detection:
    amount-threshold: 10000.00
    frequency-threshold: 5
    duplicate-check-window-hours: 24
```

## Testing

Run all tests:

```bash
./gradlew test
```

## Project Structure

```
src/
├── main/
│   ├── java/com/healthpay/
│   │   ├── model/              # Domain models
│   │   ├── repository/         # Data repositories
│   │   ├── service/            # Business logic
│   │   └── graphql/            # GraphQL resolvers
│   └── resources/
│       ├── schema/             # GraphQL schema
│       └── application.yml     # Configuration
└── test/
    └── java/com/healthpay/     # Unit tests
```

## Federation Support

This service implements Apollo Federation v2.0 specification, enabling it to be part of a larger federated GraphQL architecture. Entity types are marked with `@key` directives and can be extended by other services.

## Example Usage

### Detect Fraud in a High-Value Claim

```bash
# Submit a high-value claim
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { submitClaim(patientId: \"patient-999\", providerId: \"provider-999\", amount: \"25000.00\", diagnosisCodes: [\"D999\"], procedureCodes: [\"P999\"], serviceDate: \"2024-01-20\") { id } }"
  }'

# Process the claim - will trigger fraud alert
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { processClaim(claimId: \"CLAIM_ID_FROM_ABOVE\") { status fraudAlerts { fraudType riskScore indicators } } }"
  }'
```

### Detect Payment Errors

```bash
# Submit a claim with invalid data
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { submitClaim(patientId: \"patient-123\", providerId: \"provider-456\", amount: \"-100.00\", diagnosisCodes: [], procedureCodes: [\"P001\"], serviceDate: \"2024-01-15\") { id } }"
  }'

# Process the claim - will detect payment errors
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { processClaim(claimId: \"CLAIM_ID_FROM_ABOVE\") { status paymentErrors { errorType severity description } } }"
  }'
```

## License

MIT License

## Contributing

Contributions are welcome! Please submit pull requests with detailed descriptions of changes.