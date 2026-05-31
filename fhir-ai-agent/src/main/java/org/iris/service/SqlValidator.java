package org.iris.service;

import java.util.Locale;
import java.util.Set;

import org.jdbi.v3.core.Jdbi;
import org.jboss.logging.Logger;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class SqlValidator {

    private static final Logger log = Logger.getLogger(SqlValidator.class);

    private static final Set<String> FORBIDDEN_KEYWORDS = Set.of(
            "insert", "update", "delete", "merge", "drop", "alter",
            "create", "truncate", "grant", "revoke", "execute", "exec", "call"
    );

    @Inject
    Jdbi jdbi;

    public void validateReadOnlySelect(String sql) {
        validateSafety(sql);
        validateSqlCompiles(sql);
    }

    private void validateSafety(String sql) {
        
        log.infof("Validating SQL: %s", sql);

        if (sql == null || sql.isBlank()) {
            throw new IllegalArgumentException("SQL is empty");
        }

        String lower = sql.trim().toLowerCase(Locale.ROOT);

        if (!lower.startsWith("select") ) {
            throw new IllegalArgumentException("Only SELECT queries are allowed.");
        }

        if (lower.contains(";") || lower.contains("--") || lower.contains("/*") || lower.contains("*/")) {
            throw new IllegalArgumentException("Multiple statements or comments are not allowed.");
        }

        if (!lower.contains("hsfhir_x0001_s")
                && !lower.contains("hsfhir_x0001_r")
                && !lower.contains("dc.")) {
            throw new IllegalArgumentException("SQL must target allowed FHIR schemas.");
        }

        String normalized = lower.replaceAll("[^a-z0-9_]", " ");
        String[] words = normalized.split("\\s+");

        for (String word : words) {
            if (FORBIDDEN_KEYWORDS.contains(word) || word.startsWith("xp_")) {
                throw new IllegalArgumentException("SQL contains keyword not allowed: " + word);
            }
        }
    }

    private void validateSqlCompiles(String sql) {
        try {
            jdbi.useHandle(handle ->
                    handle.createQuery(sql)
                            .setMaxRows(1)
                            .mapToMap()
                            .findFirst()
            );
        } catch (Exception e) {
            log.warnf(e, "SQL failed compilation/execution validation");
            throw new IllegalArgumentException("SQL is not valid for IRIS: " + e.getMessage(), e);
        }
    }
}