package org.iris.ia.tools;


import org.iris.ia.dto.SqlFhirBuildResult;
import org.iris.ia.dto.SqlQueryResponse;
import org.iris.ia.flow.FlowSqlExecuteAgents;
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
import org.iris.service.SqlExecutor;
import java.util.Collections;
import org.jboss.logging.Logger;

@ApplicationScoped
public class FhirSqlTool {

    private static final Logger LOG = Logger.getLogger(FhirSqlTool.class);

    @Inject
    SqlValidator sqlValidator;

    @Inject
    SqlExecutor sqlExecutor;

    @Inject
    FlowSqlExecuteAgents flow;

    @Tool("""
    Use this tool to answer questions about FHIR data.
    """)
    public SqlFhirBuildResult queryFhir(String question) {
        LOG.infof("queryFhir called with question: %s", question);
        String sql = flow.buildSql(question);

        return runSql(sql);
    }

    public SqlFhirBuildResult runSql(String sql) {
        LOG.infof("runSql called (len=%d)", sql == null ? 0 : sql.length());
        try {
            sqlValidator.validateReadOnlySelect(sql);
        } catch (Exception ex) {
            LOG.warnf(ex, "SQL validation failed: %s", ex.getMessage());
            return new SqlFhirBuildResult(false, sql, new SqlQueryResponse(Collections.emptyList(), "Validation failed: " + ex.getMessage()));
        }

        try {
            List<Map<String, Object>> rows = sqlExecutor.execute(sql);
            LOG.infof("SQL executed, row count=%d", rows == null ? 0 : rows.size());
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
