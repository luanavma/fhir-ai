package org.iris.ia.tools;

import java.util.List;
import java.util.stream.Collectors;

import org.iris.ia.dto.TerminologyResult;

import dev.langchain4j.agent.tool.Tool;
import jakarta.annotation.Nonnull;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.persistence.EntityManager;

@ApplicationScoped
public class TerminologyTool {

    @Inject
    EntityManager em;

    @Nonnull
    @SuppressWarnings("null")
    @Tool("""
        Use this tool to discover FHIR terminology codes from the database.
        It returns distinct code/text values for Condition and Observation resources.
        Use it before generating disease-specific SQL when the coding representation is unknown.
        """)
    public List<TerminologyResult> discoverTerminology() {
        String sql = """
                SELECT
                    ResourceType,
                    GetJSON(GetJSON(ResourceString,'code'),'coding') AS CodingJson,
                    GetProp(GetJSON(ResourceString,'code'),'text') AS TextValue
                FROM HSFHIR_X0001_R.Rsrc
                WHERE ResourceType IN ('Condition','Observation')
                GROUP BY
                    ResourceType,
                    GetJSON(GetJSON(ResourceString,'code'),'coding'),
                    GetProp(GetJSON(ResourceString,'code'),'text')
                ORDER BY
                    ResourceType,
                    TextValue
                """;

        @SuppressWarnings("unchecked")
        List<Object[]> rows = em.createNativeQuery(sql).getResultList();

        return rows.stream()
        .map(row -> new TerminologyResult(
                row[0] == null ? null : (String) row[0],
                row[1] == null ? null : row[1].toString(),
                row[2] == null ? null : row[2].toString()
        ))
        .toList();
    }
}
