package com.healthpay.graphql.scalar;

import graphql.language.StringValue;
import graphql.schema.Coercing;
import graphql.schema.CoercingParseLiteralException;
import graphql.schema.CoercingParseValueException;
import graphql.schema.CoercingSerializeException;
import graphql.schema.GraphQLScalarType;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.graphql.execution.RuntimeWiringConfigurer;

import java.math.BigDecimal;

@Configuration
public class ScalarConfiguration {

    @Bean
    public RuntimeWiringConfigurer runtimeWiringConfigurer() {
        return wiringBuilder -> wiringBuilder
                .scalar(bigDecimalScalar());
    }

    private GraphQLScalarType bigDecimalScalar() {
        return GraphQLScalarType.newScalar()
                .name("BigDecimal")
                .description("A custom scalar that represents BigDecimal values")
                .coercing(new Coercing<BigDecimal, String>() {
                    @Override
                    public String serialize(Object dataFetcherResult) throws CoercingSerializeException {
                        if (dataFetcherResult instanceof BigDecimal) {
                            return ((BigDecimal) dataFetcherResult).toPlainString();
                        }
                        throw new CoercingSerializeException("Expected a BigDecimal object.");
                    }

                    @Override
                    public BigDecimal parseValue(Object input) throws CoercingParseValueException {
                        try {
                            if (input instanceof String) {
                                return new BigDecimal((String) input);
                            } else if (input instanceof Number) {
                                return BigDecimal.valueOf(((Number) input).doubleValue());
                            }
                            throw new CoercingParseValueException("Expected a String or Number");
                        } catch (Exception e) {
                            throw new CoercingParseValueException("Unable to parse value to BigDecimal", e);
                        }
                    }

                    @Override
                    public BigDecimal parseLiteral(Object input) throws CoercingParseLiteralException {
                        if (input instanceof StringValue) {
                            try {
                                return new BigDecimal(((StringValue) input).getValue());
                            } catch (Exception e) {
                                throw new CoercingParseLiteralException("Unable to parse literal to BigDecimal", e);
                            }
                        }
                        throw new CoercingParseLiteralException("Expected a StringValue.");
                    }
                })
                .build();
    }
}
