package org.iris.ia.tools;

import org.iris.service.SqlValidator;

import dev.langchain4j.agent.tool.Tool;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class ValidSqlTool {

    @Inject
    SqlValidator sqlValidator;

    @Tool("""
            Use this tool to validate that a SQL query is read-only and only contains SELECT statements.
            If the SQL is valid, return it as-is.
            If the SQL is invalid, return an error message indicating the reason for invalidation.
            """)
    public String validSql(String sql) {
        String result;

        try {
            sqlValidator.validateReadOnlySelect(sql);
            result = sql;
        } catch (Exception ex) {
            result = "Validation failed: " + ex.getMessage();
        }

        return result;
    }
}
