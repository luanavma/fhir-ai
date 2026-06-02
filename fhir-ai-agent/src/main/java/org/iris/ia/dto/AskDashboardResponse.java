package org.iris.ia.dto;

import java.util.List;

public record AskDashboardResponse(
        String answer,
        List<RegionData> regions,
        AISummary summary
) {
}