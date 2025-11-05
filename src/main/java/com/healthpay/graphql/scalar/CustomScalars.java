package com.healthpay.graphql.scalar;

import com.netflix.graphql.dgs.DgsComponent;
import com.netflix.graphql.dgs.DgsRuntimeWiring;
import graphql.language.StringValue;
import graphql.schema.Coercing;
import graphql.schema.CoercingParseLiteralException;
import graphql.schema.CoercingParseValueException;
import graphql.schema.CoercingSerializeException;
import graphql.schema.GraphQLScalarType;
import graphql.schema.idl.RuntimeWiring;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@DgsComponent
public class CustomScalars {

    @DgsRuntimeWiring
    public RuntimeWiring.Builder addScalars(RuntimeWiring.Builder builder) {
        return builder
                .scalar(bigDecimalScalar())
                .scalar(dateTimeScalar());
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

    private GraphQLScalarType dateTimeScalar() {
        return GraphQLScalarType.newScalar()
                .name("DateTime")
                .description("A custom scalar that represents LocalDateTime values")
                .coercing(new Coercing<LocalDateTime, String>() {
                    private final DateTimeFormatter formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME;

                    @Override
                    public String serialize(Object dataFetcherResult) throws CoercingSerializeException {
                        if (dataFetcherResult instanceof LocalDateTime) {
                            return ((LocalDateTime) dataFetcherResult).format(formatter);
                        }
                        throw new CoercingSerializeException("Expected a LocalDateTime object.");
                    }

                    @Override
                    public LocalDateTime parseValue(Object input) throws CoercingParseValueException {
                        try {
                            if (input instanceof String) {
                                return LocalDateTime.parse((String) input, formatter);
                            }
                            throw new CoercingParseValueException("Expected a String");
                        } catch (Exception e) {
                            throw new CoercingParseValueException("Unable to parse value to LocalDateTime", e);
                        }
                    }

                    @Override
                    public LocalDateTime parseLiteral(Object input) throws CoercingParseLiteralException {
                        if (input instanceof StringValue) {
                            try {
                                return LocalDateTime.parse(((StringValue) input).getValue(), formatter);
                            } catch (Exception e) {
                                throw new CoercingParseLiteralException("Unable to parse literal to LocalDateTime", e);
                            }
                        }
                        throw new CoercingParseLiteralException("Expected a StringValue.");
                    }
                })
                .build();
    }
}
