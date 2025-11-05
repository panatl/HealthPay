import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import { ApolloGateway, IntrospectAndCompose } from '@apollo/gateway';

const gateway = new ApolloGateway({
  supergraphSdl: new IntrospectAndCompose({
    subgraphs: [
      {
        name: 'claims',
        url: process.env.CLAIMS_SERVICE_URL || 'http://localhost:8081/graphql'
      },
      {
        name: 'fraud',
        url: process.env.FRAUD_SERVICE_URL || 'http://localhost:8082/graphql'
      },
      {
        name: 'analytics',
        url: process.env.ANALYTICS_SERVICE_URL || 'http://localhost:8083/graphql'
      }
    ]
  })
});

const server = new ApolloServer({
  gateway,
  subscriptions: false,
});

const { url } = await startStandaloneServer(server, {
  listen: { port: parseInt(process.env.PORT || '4000') }
});

console.log(`🚀 Apollo Gateway ready at ${url}`);
console.log(`📊 Federation Spec: v2.9`);
console.log(`🔗 Connected subgraphs:`);
console.log(`   - Claims Service: ${process.env.CLAIMS_SERVICE_URL || 'http://localhost:8081/graphql'}`);
console.log(`   - Fraud Detection Service: ${process.env.FRAUD_SERVICE_URL || 'http://localhost:8082/graphql'}`);
console.log(`   - Analytics Service: ${process.env.ANALYTICS_SERVICE_URL || 'http://localhost:8083/graphql'}`);
