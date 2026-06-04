# 📊  project-name
 > Transform healthcare data into actionable insights through natural language conversations, geospatial visualization, and AI-assisted epidemiological investigation.

## 📋 About

project-name is an intelligent epidemiological analysis platform designed to help healthcare professionals, researchers, and public health teams explore FHIR-based clinical data through a conversational interface.

Instead of manually querying databases or navigating complex healthcare records, users can ask questions in natural language and receive answers grounded in real FHIR resources and epidemiological datasets.

## ✨ Features

Ask questions such as:

- "Show respiratory disease trends in the last 12 weeks."
- "Which regions reported the highest dengue incidence this month?"
- "Tell me about COVID-19 cases in Brazil"

The AI agent translates questions into validated queries and retrieves data directly from FHIR resources.

- 💬 **Conversational Interface** — Ask epidemiological questions in natural language, maintaining session context via `chatId`
- 🗺️ **Geospatial Heatmaps** — Leaflet-based visualization of disease distribution across regions
- 🔍 **Hybrid Search** — Combines FHIR SQL execution with semantic vector search for richer answers
- 🤖 **AI Agent (LangChain4j)** — Intelligent agent that decides when to query FHIR SQL vs. vector store
- 📊 **RAG Pipeline** — Retrieval-Augmented Generation over vectorized FHIR resources
- 🏥 **FHIR R4 Compliant** — Built on top of InterSystems IRIS for Health FHIR repository


🔒 Controlled Data Access

For safety and auditability:

The AI agent never executes arbitrary SQL.
All database access is mediated through predefined tools.
Queries are validated before execution.
Results are generated exclusively from real healthcare data.

This approach follows the same principle used by modern healthcare AI systems that rely on controlled FHIR access instead of unrestricted database interaction.


## 🚀 Getting Started

### Prerequisites

Make sure you have installed:
- Git
- Docker
- Docker Compose
- OpenAI API Key

📂 Clone Repository
```bash
git clone https://github.com/luanavma/fhir-ai.git
```

```bash
cd fhir-ai
```

⚙️ Configure Environment Variables

- Before starting the stack, define the `OPENAI_API_KEY` environment variable on your machine.

    **Linux / macOS**

    ```bash
    export OPENAI_API_KEY=your_openai_api_key_here
    ```

### ⚡ Start the Application

- From the project root directory, run:

    ```bash
      docker compose up --build
    ```
The first startup may take several minutes while Docker downloads the required images.

- Docker Compose will automatically:

  - 🟦 Build and start the InterSystems IRIS container
  - ⏳ Wait for IRIS to become healthy
  - 🖥️ Start the Quarkus backend (AI agent + SQL analytics)
  - 🗄️ Start the Angular frontend (conversational UI)


### Accessing the Services 🌐

- Once the stack is running:
  - 🤖 **Frontend (Conversational UI):** <http://localhost:4200>
  - 📊 **Backend API (Quarkus / Swagger UI):** <http://localhost:8080/swagger-ui/>
  - 🗄️ **InterSystems IRIS Management Portal:** -> <http://localhost:52773/csp/sys/UtilHome.csp>


## Architecture

## authors

- [Davi Massaru Teixeira Muta](https://community.intersystems.com/user/davimassaru-teixeiramuta)
  - Linkedin: https://www.linkedin.com/in/davimassarumuta/
  - Github: https://github.com/Davi-Massaru
  - intersystems community: https://community.intersystems.com/user/davimassaru-teixeiramuta

- [Luana Vieira Machado]()
  - Linkedin: https://linkedin.com/in/luana-vieira-machado
  - Github: https://github.com/luanavma/
  - intersystems community: https://community.intersystems.com/user/luana-machado