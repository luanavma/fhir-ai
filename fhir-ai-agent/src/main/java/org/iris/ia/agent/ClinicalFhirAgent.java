package org.iris.ia.agent;

import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import io.quarkiverse.langchain4j.RegisterAiService;
import jakarta.enterprise.context.ApplicationScoped;

import org.iris.ia.tools.DateTools;
import org.iris.ia.tools.FhirSqlTool;
import org.iris.ia.tools.TerminologyTool;

@ApplicationScoped
@RegisterAiService(tools = {
        FhirSqlTool.class,
        TerminologyTool.class,
        DateTools.class
})
public interface ClinicalFhirAgent {

    @SystemMessage("""
    You are a FHIR IRIS assistant.
    The steps are:
        1 - Generate SQL query with the FhirSqlTool to answer the question based on the HSFHIR_X0001_S/R Tables.
        2 - Analyze the results and generate a final answer to the user.
    """)
    @UserMessage("""
    Generate a analysis of the question: {{question}}
    """)
    String ask(String question);
}
