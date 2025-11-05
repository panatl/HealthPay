# HealthPay - Spring Reactive Microservices with Apollo GraphQL Federation 2.9

## Project Structure

```
HealthPay/
├── apollo-gateway/                 # Apollo Federation Gateway
│   ├── src/
│   │   └── index.js               # Gateway configuration with Federation 2.9
│   ├── package.json
│   └── Dockerfile
│
├── claims-service/                 # Claims & Payment Integrity Service
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/healthpay/
│   │   │   │   ├── model/         # Domain models
│   │   │   │   ├── service/       # Business logic
│   │   │   │   ├── resolver/      # GraphQL resolvers
│   │   │   │   ├── repository/    # MongoDB repositories
│   │   │   │   └── ClaimsServiceApplication.java
│   │   │   └── resources/
│   │   │       ├── schema/
│   │   │       │   └── claims.graphqls  # GraphQL schema with Federation
│   │   │       └── application.yml
│   │   └── test/
│   ├── pom.xml
│   └── Dockerfile
│
├── fraud-detection-service/        # Fraud, Waste, and Abuse Detection
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/healthpay/
│   │   │   │   ├── model/
│   │   │   │   ├── service/
│   │   │   │   ├── resolver/
│   │   │   │   └── FraudDetectionServiceApplication.java
│   │   │   └── resources/
│   │   │       ├── schema/
│   │   │       │   └── fraud.graphqls
│   │   │       └── application.yml
│   │   └── test/
│   ├── pom.xml
│   └── Dockerfile
│
├── analytics-service/              # Analytics and Reporting
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/healthpay/
│   │   │   │   ├── model/
│   │   │   │   ├── service/
│   │   │   │   ├── resolver/
│   │   │   │   └── AnalyticsServiceApplication.java
│   │   │   └── resources/
│   │   │       ├── schema/
│   │   │       │   └── analytics.graphqls
│   │   │       └── application.yml
│   │   └── test/
│   ├── pom.xml
│   └── Dockerfile
│
├── docker-compose.yml              # Docker Compose orchestration
├── README.md                       # Main documentation
├── API_EXAMPLES.md                 # API usage examples
└── .gitignore

```

## Technology Stack

### Backend Services
- **Spring Boot 3.2.0** - Application framework
- **Spring WebFlux** - Reactive web framework
- **Netflix DGS (Domain Graph Service) 8.1.1** - GraphQL framework
- **Apollo Federation 4.3.0** - GraphQL federation support
- **Spring Data MongoDB Reactive** - Reactive MongoDB integration
- **Project Lombok** - Boilerplate reduction
- **Java 17** - Programming language

### API Gateway
- **Apollo Server 4.10.0** - GraphQL server
- **Apollo Gateway 2.9.0** - Federation gateway with Spec 2.9
- **Node.js 20** - Runtime environment

### Database
- **MongoDB 7.0** - NoSQL database for reactive operations

### Build & Deployment
- **Maven 3.8+** - Build tool
- **Docker & Docker Compose** - Containerization
- **Alpine Linux** - Base Docker images

## Microservices

### 1. Claims Service (Port 8081)
**Responsibilities:**
- Payment integrity analysis
- Claims validation
- Overpayment/underpayment detection
- Pricing error detection
- Risk scoring

**GraphQL Schema:** Federation 2.9 compliant
- `@key` directives on Claim and ClaimAnalysisResult
- Mutations for claim submission
- Queries for claim analysis

### 2. Fraud Detection Service (Port 8082)
**Responsibilities:**
- Fraud pattern detection
- High-volume billing alerts
- Doctor shopping detection
- Provider risk scoring
- Duplicate billing identification

**GraphQL Schema:** Federation 2.9 compliant
- `@key` directive on FraudAlert
- `@external` reference to Claim
- Queries for fraud analysis

### 3. Analytics Service (Port 8083)
**Responsibilities:**
- Analytics summary generation
- Top provider analysis
- Payment accuracy calculations
- Cost efficiency metrics
- Reporting

**GraphQL Schema:** Federation 2.9 compliant
- Aggregation queries
- Statistical analysis
- Cross-service data composition

### 4. Apollo Gateway (Port 4000)
**Responsibilities:**
- Unified GraphQL API
- Schema composition
- Query planning
- Service orchestration
- Federation 2.9 support

**Features:**
- Introspection and compose
- Entity resolution
- Distributed query execution

## Apollo Federation 2.9

The platform implements Apollo Federation Specification 2.9 with:

### Directives
- `@key`: Define entity keys for type resolution
- `@external`: Mark fields from other subgraphs
- `@shareable`: Allow fields to be resolved by multiple subgraphs
- `@link`: Import federation directives

### Type Extensions
Services extend types from other services:
```graphql
extend schema @link(url: "https://specs.apollo.dev/federation/v2.9", 
                   import: ["@key", "@shareable", "@external"])

type Claim @key(fields: "claimId") {
  claimId: ID!
  # ...
}
```

### Entity Resolution
The gateway automatically resolves entities across services using the `@key` directive.

## Reactive Programming

All services use reactive programming with:
- **Mono<T>**: Single value or empty
- **Flux<T>**: Stream of 0 to N values
- **Non-blocking I/O**: Efficient resource utilization
- **Backpressure handling**: Flow control

## API Communication Flow

```
Client
  ↓ GraphQL Query
Apollo Gateway (Port 4000)
  ├─→ Claims Service (Port 8081)
  ├─→ Fraud Detection (Port 8082)
  └─→ Analytics Service (Port 8083)
       ↓ All services use
     MongoDB (Port 27017)
```

## Building from Source

### Prerequisites
- JDK 17+
- Maven 3.8+
- Node.js 20+
- Docker 20+

### Build All Services

```bash
# Claims Service
cd claims-service
mvn clean package

# Fraud Detection Service
cd fraud-detection-service
mvn clean package

# Analytics Service
cd analytics-service
mvn clean package

# Apollo Gateway
cd apollo-gateway
npm install
```

### Run with Docker Compose

```bash
docker-compose up --build
```

## Configuration

### Service Ports
- Claims Service: 8081
- Fraud Detection: 8082
- Analytics Service: 8083
- Apollo Gateway: 4000
- MongoDB: 27017

### Environment Variables
Each service supports configuration via environment variables:
- `SPRING_DATA_MONGODB_URI`: MongoDB connection string
- `SERVER_PORT`: Service port
- `CLAIMS_SERVICE_URL`: Claims service GraphQL endpoint (gateway)
- `FRAUD_SERVICE_URL`: Fraud service GraphQL endpoint (gateway)
- `ANALYTICS_SERVICE_URL`: Analytics service GraphQL endpoint (gateway)

## Development

### Running Individual Services

```bash
# Start MongoDB
docker run -d -p 27017:27017 mongo:7.0

# Start Claims Service
cd claims-service
mvn spring-boot:run

# Start Fraud Detection
cd fraud-detection-service
mvn spring-boot:run

# Start Analytics Service
cd analytics-service
mvn spring-boot:run

# Start Apollo Gateway
cd apollo-gateway
npm start
```

### GraphQL Endpoints

Each service exposes its own GraphQL endpoint:
- http://localhost:8081/graphql (Claims)
- http://localhost:8082/graphql (Fraud)
- http://localhost:8083/graphql (Analytics)

Unified endpoint through gateway:
- http://localhost:4000/graphql

## Testing

Run tests for each service:

```bash
cd <service-name>
mvn test
```

## Monitoring

Each service includes:
- Spring Boot Actuator endpoints
- Health checks at `/actuator/health`
- Metrics at `/actuator/metrics`
- GraphQL schema introspection

## Deployment

### Docker Compose (Development)
```bash
docker-compose up -d
```

### Kubernetes (Production)
Use provided Docker images with Kubernetes manifests.

## Future Enhancements

- JWT authentication & authorization
- Distributed tracing with OpenTelemetry
- Caching with Redis
- Event-driven architecture with Kafka
- Machine learning models for fraud detection
- Real-time subscriptions with GraphQL
- API rate limiting
- Dashboard UI with React

## License

MIT License
