package org.iris.ia.dto;

public record RegionData(
        String city,
        Integer totalCases,
        String mainSymptoms,
        Double latitude,
        Double longitude
) {
}
