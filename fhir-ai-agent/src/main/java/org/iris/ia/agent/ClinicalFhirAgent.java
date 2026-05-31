package org.iris.ia.agent;

import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import io.quarkiverse.langchain4j.RegisterAiService;
import jakarta.enterprise.context.ApplicationScoped;

import org.iris.ia.tools.DateTools;
import org.iris.ia.tools.FhirSqlTool;

@ApplicationScoped
@RegisterAiService(tools = {
        FhirSqlTool.class,
        DateTools.class
})
public interface ClinicalFhirAgent {

    @SystemMessage("""
    Você é um assistente FHIR.
    Quando precisar consultar dados, use a ferramenta FhirSqlTool.
    Responda em português.
    """)
    @UserMessage("""
    Pergunta do usuário:
    {{question}}
    """)
    String ask(String question);
}
