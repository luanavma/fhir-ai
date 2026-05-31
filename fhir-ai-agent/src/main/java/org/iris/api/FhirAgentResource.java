package org.iris.api;

import org.iris.ia.agent.ClinicalFhirAgent;
import org.iris.ia.dto.AskRequest;
import org.iris.ia.dto.AskResponse;

import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/fhir-agent")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class FhirAgentResource {

    @Inject
    ClinicalFhirAgent clinicalFhirAgent;

    @POST
    @Path("/ask")
    public AskResponse ask(AskRequest request) {
        String answer = clinicalFhirAgent.ask(request.question());

        return new AskResponse(
                request.chatId(),
                request.question(),
                answer,
                null
        );
    }
}
