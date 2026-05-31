package org.iris.ia.tools;


import org.iris.ia.dto.SqlFhirBuildResult;
import org.iris.ia.dto.SqlQueryResponse;
import org.iris.service.SqlValidator;

import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.ArrayList;
import java.util.LinkedHashMap;

import dev.langchain4j.agent.tool.Tool;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.persistence.EntityManager;
import java.util.Collections;
import org.jboss.logging.Logger;

@ApplicationScoped
public class FhirSqlTool {

    private static final Logger LOG = Logger.getLogger(FhirSqlTool.class);

    @Inject
    SqlValidator sqlValidator;

    @Inject
    EntityManager em;

    @Tool("""
        Use this tool to run read-only SQL SELECT queries against the FHIR database.
        Always validate the SQL with the provided SqlValidator before executing.
        If the SQL is invalid, return an error message instead of executing.
    """)
    public SqlFhirBuildResult runSql(String sql) {
        LOG.infof("runSql called (len=%d)", sql == null ? 0 : sql.length());
        try {
            sqlValidator.validateReadOnlySelect(sql);
        } catch (Exception ex) {
            LOG.warnf(ex, "SQL validation failed: %s", ex.getMessage());
            return new SqlFhirBuildResult(false, sql, new SqlQueryResponse(Collections.emptyList(), "Validation failed: " + ex.getMessage()));
        }

        try {
            @SuppressWarnings("unchecked")
            List<Object[]> raw = (List<Object[]>) em.createNativeQuery(sql).setMaxResults(200).getResultList();
            LOG.infof("SQL executed, raw result count=%d", raw == null ? 0 : raw.size());

            List<String> colNames = extractSelectColumns(sql);
            List<Map<String, Object>> rows = new ArrayList<>();

            for (Object[] r : raw) {
                Map<String, Object> map = new LinkedHashMap<>();
                for (int i = 0; i < r.length; i++) {
                    String key = (i < colNames.size()) ? colNames.get(i) : ("c" + (i + 1));
                    map.put(key, r[i]);
                }
                rows.add(map);
            }
            LOG.infof("Returning %d rows", rows.size());
            return new SqlFhirBuildResult(true, sql, new SqlQueryResponse(rows, null));
        } catch (Exception ex) {
            LOG.errorf(ex, "Execution failed for SQL: %s", ex.getMessage());
            return new SqlFhirBuildResult(false, sql, new SqlQueryResponse(Collections.emptyList(), "Execution failed: " + ex.getMessage()));
        }
    }

    private List<String> extractSelectColumns(String sql) {
        try {
            Pattern p = Pattern.compile("(?is)select\\s+(.*?)\\s+from\\b");
            Matcher m = p.matcher(sql);
            if (!m.find()) return List.of();
            String cols = m.group(1);
            String[] parts = cols.split(",");
            List<String> names = new ArrayList<>();
            for (String part : parts) {
                String s = part.trim();
                s = s.replaceAll("\\(|\\)", "");
                Matcher asM = Pattern.compile("(?i)\\s+as\\s+(\\S+)").matcher(s);
                if (asM.find()) {
                    names.add(normalizeName(asM.group(1)));
                    continue;
                }
                String[] toks = s.split("\\s+");
                String last = toks[toks.length - 1];
                last = last.replaceAll("[\"`\\[\\]]", "");
                names.add(normalizeName(last));
            }
            return names;
        } catch (Exception ex) {
            LOG.warnf(ex, "Failed to extract select columns from SQL: %s", sql);
            return List.of();
        }
    }

    private String normalizeName(String raw) {
        String n = raw.trim();
        n = n.replaceAll("[^a-zA-Z0-9]", "_").toLowerCase();
        if (n.isEmpty()) return "c1";
        return n;
    }

}
