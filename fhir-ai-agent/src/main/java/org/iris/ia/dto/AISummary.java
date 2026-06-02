package org.iris.ia.dto;

import java.util.List;

public record AISummary(
        String text,
        List<String> recommendations
) {
}