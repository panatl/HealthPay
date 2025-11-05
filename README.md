# HealthPay Payment Integrity Platform

A comprehensive Healthcare Payment Integrity & Analytics platform built with **Spring Boot Reactive Microservices** and **Apollo GraphQL Federation Spec 2.9**. The platform ensures claims are paid correctly by identifying overpayments, underpayments, errors, fraud, waste, and abuse in healthcare claims.

## Architecture

### Microservices Architecture
The platform is built as a federated microservices architecture using Apollo Federation 2.9:

- **Claims Service** (Port 8081) - Payment integrity analysis and claims validation
- **Fraud Detection Service** (Port 8082) - Fraud, waste, and abuse detection
- **Analytics Service** (Port 8083) - Analytics and reporting
- **Apollo Gateway** (Port 4000) - Unified GraphQL API gateway

### Technology Stack

- **Framework**: Spring Boot 3.2.0 with WebFlux (Reactive)
- **GraphQL**: Netflix DGS Framework with Apollo Federation 2.9
- **Database**: MongoDB (Reactive)
- **API Gateway**: Apollo Gateway with Federation
- **Language**: Java 17
- **Build Tool**: Maven
- **Containerization**: Docker & Docker Compose

## Features

### 🔍 Payment Integrity Analysis
- Detect overpayments and underpayments
- Identify pricing errors and calculation mistakes
- Flag duplicate services within claims
- Check for late filing and timely submission
- Validate required information (diagnosis codes, etc.)
- Calculate risk scores for claims

### 🚨 Fraud, Waste, and Abuse Detection
- Identify duplicate billing across claims
- Detect high-volume billing anomalies
- Flag provider pattern anomalies and upcoding
- Identify doctor shopping behavior
- Detect impossible service patterns
- Calculate provider fraud risk scores

### 📊 Analytics & Reporting
- Generate comprehensive analytics summaries
- Track top providers by claim amount
- Analyze most frequently billed service codes
- Calculate payment accuracy rates
- Measure cost efficiency and savings
- Monitor claims by status and type

## Getting Started

### Prerequisites
- Java 17 or higher
- Maven 3.8+
- Docker & Docker Compose
- Node.js 20+ (for Apollo Gateway)
- MongoDB 7.0

### Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/panatl/HealthPay.git
cd HealthPay
```

2. Start all services with Docker Compose:
```bash
docker-compose up --build
```

This will start:
- MongoDB on port 27017
- Claims Service on port 8081
- Fraud Detection Service on port 8082
- Analytics Service on port 8083
- Apollo Gateway on port 4000

3. Access the GraphQL Playground:
```
http://localhost:4000/graphql
```

### Local Development

#### Build Individual Services

```bash
# Claims Service
cd claims-service
mvn clean install
mvn spring-boot:run

# Fraud Detection Service
cd fraud-detection-service
mvn clean install
mvn spring-boot:run

# Analytics Service
cd analytics-service
mvn clean install
mvn spring-boot:run

# Apollo Gateway
cd apollo-gateway
npm install
npm start
```

## GraphQL API

The platform exposes a unified GraphQL API through Apollo Gateway with Federation 2.9 support.

### Example Queries

#### Analyze a Claim

```graphql
mutation AnalyzeClaim {
  analyzeClaim(input: {
    claimId: "CLM001"
    patientId: "PAT001"
    providerId: "PRV001"
    claimType: OUTPATIENT
    serviceDate: "2024-01-15T10:00:00Z"
    submissionDate: "2024-01-20T10:00:00Z"
    services: [{
      code: "99213"
      description: "Office visit"
      units: 1
      unitPrice: 150.00
    }]
    claimedAmount: 150.00
    allowedAmount: 100.00
    paidAmount: 150.00
    status: APPROVED
    diagnosisCodes: ["I10"]
  }) {
    claimId
    isValid
    riskScore
    totalEstimatedImpact
    issues {
      issueType
      severity
      description
      estimatedImpact
      recommendation
    }
  }
}
```

#### Detect Fraud Patterns

```graphql
query AnalyzeFraud {
  analyzeFraud(claims: [
    {
      claimId: "CLM001"
      patientId: "PAT001"
      providerId: "PRV001"
      claimType: PHARMACY
      serviceDate: "2024-01-15T10:00:00Z"
      submissionDate: "2024-01-20T10:00:00Z"
      services: [{code: "J2001", description: "Medication", units: 1, unitPrice: 150.00}]
      claimedAmount: 150.00
      diagnosisCodes: ["M79.3"]
    }
  ]) {
    alertId
    alertType
    confidenceScore
    patternDescription
    status
    claimIds
  }
}
```

#### Generate Analytics Summary

```graphql
query GetAnalytics {
  getAnalyticsSummary(claims: [
    {
      claimId: "CLM001"
      patientId: "PAT001"
      providerId: "PRV001"
      claimType: OUTPATIENT
      claimedAmount: 150.00
      paidAmount: 150.00
      status: APPROVED
    }
  ]) {
    totalClaims
    totalClaimedAmount
    totalPaidAmount
    averageRiskScore
    claimsByStatus {
      status
      count
    }
    claimsByType {
      claimType
      count
    }
  }
}
```

### Get Provider Risk Score

```graphql
query GetProviderRisk {
  getProviderRiskScore(providerId: "PRV001") {
    providerId
    riskScore
    riskLevel
  }
}
```

## Apollo Federation

The platform implements Apollo Federation 2.9 specification with:

- **`@key` directive**: Entity key definitions for federated types
- **`@external` directive**: External field references across subgraphs
- **`@shareable` directive**: Shareable fields across services
- **Type extensions**: Extending types from other subgraphs

### Federated Schema Example

```graphql
extend schema @link(url: "https://specs.apollo.dev/federation/v2.9", 
                   import: ["@key", "@shareable", "@external"])

type Claim @key(fields: "claimId") {
  claimId: ID!
  patientId: String!
  # ... other fields
}
```

## Service Endpoints

### Individual Service GraphQL Endpoints

- **Claims Service**: http://localhost:8081/graphql
- **Fraud Detection**: http://localhost:8082/graphql
- **Analytics Service**: http://localhost:8083/graphql

### Unified Gateway

- **Apollo Gateway**: http://localhost:4000/graphql
- **GraphQL Playground**: http://localhost:4000

## Configuration

Each service can be configured via `application.yml`:

```yaml
spring:
  application:
    name: claims-service
  data:
    mongodb:
      uri: mongodb://localhost:27017/healthpay

server:
  port: 8081

dgs:
  graphql:
    path: /graphql
```

## Testing

Run tests for each service:

```bash
# Claims Service
cd claims-service
mvn test

# Fraud Detection Service
cd fraud-detection-service
mvn test

# Analytics Service
cd analytics-service
mvn test
```

## Deployment

### Docker Compose

```bash
docker-compose up -d
```

### Kubernetes

Kubernetes manifests can be generated using the provided Docker images.

## Monitoring

- Spring Boot Actuator endpoints available at `/actuator`
- GraphQL schema introspection at `/graphql`
- Health checks at `/actuator/health`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.