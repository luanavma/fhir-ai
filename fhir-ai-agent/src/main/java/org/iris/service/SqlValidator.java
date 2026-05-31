package org.iris.service;

import java.util.Locale;

import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class SqlValidator {

    public void validateReadOnlySelect(String sql) {
        if (sql == null || sql.isBlank()) {
            throw new IllegalArgumentException("SQL is empty");
        }

        String s = sql.trim();
        String lower = s.toLowerCase(Locale.ROOT);

        // evitar múltiplas statements
        if (lower.contains(";") || lower.contains("--") || lower.contains("/*") || lower.contains("*/")) {
            throw new IllegalArgumentException("SQL contains keyword not allowed: ';' or '--' or '/*' or '*/'");
        }

        if (!lower.startsWith("select")) {
            throw new IllegalArgumentException("SQL contains keyword not allowed: '" + lower.substring(0, Math.min(6, lower.length())) + "'");
        }

        // bloquear DML/DDL mais comuns
        String[] forbidden = { "insert ", "update ", "delete ", "merge ", "drop ", "alter ", "create ", "truncate ",
                "grant ", "revoke ", "execute ", "call ", "xp_" };
        var sqlWords = lower.split("\\s+");
        for (String f : forbidden) {
            if (containsWord(sqlWords, f.trim())) {
                throw new IllegalArgumentException("SQL contains keyword not allowed: " + f.trim());
            }
        }
    }

    private boolean containsWord(String[] words, String word) {
        for (String w : words) {
            if (w.equals(word)) {
                return true;
            }
        }
        return false;
    }
}
