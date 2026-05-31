package org.iris.ia.dto;

public record TerminologyResult(
        String resourceType,
        String codingJson,
        String textValue
    ){
}