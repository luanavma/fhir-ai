package org.iris.ia.dto;

import java.util.List;
import java.util.Map;

public record SqlQueryResponse(
        List<Map<String, Object>> rows,
        String error) {
}
