package org.iris.ia.flow;

import java.util.List;

import org.iris.ia.agent.SQLFhirBuilderAgent;
import org.iris.ia.dto.TerminologyResult;
import org.iris.ia.tools.TerminologyTool;
import org.iris.service.SqlValidator;

import jakarta.inject.Inject;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class FlowSqlExecuteAgents {
    
    @Inject
    TerminologyTool terminologyTool;

    @Inject
    SQLFhirBuilderAgent sqlFhirBuilderAgent;
    
    @Inject
    SqlValidator sqlValidator;

    public String buildSql(String question) {
        String questionoriginal = question;
        String sql = "";
        Integer tentativeSql = 0;
        Boolean sqlValid = false;
        List<TerminologyResult> terminology = terminologyTool.discoverTerminology(question);

        while (tentativeSql < 5 && !sqlValid) {
            tentativeSql++;
            sql = sqlFhirBuilderAgent.buildSql(
                question,
                terminology
            );
            try {
                sqlValidator.validateReadOnlySelect(sql);
                sqlValid = true;
                
            } catch (Exception ex) {
                question = String.format("""
                To answer the question: %s
                The following SQL generated is invalid: %s
                The error is: %s
                Please generate a new SQL that is valid and only contains read-only SELECT statements.
                """, questionoriginal, sql, ex.getMessage());
            }
        }

        return sql;
    }

}
