# Architecture

## System Overview

CultureBridge AI is a multi-agent system that adapts e-commerce storefront experiences based on cultural behavioral dimensions. The system uses Microsoft Agent Framework for orchestration and Azure AI Foundry / Azure OpenAI for inference.

## Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        WEB["Next.js Frontend<br/>(Azure Static Web Apps)"]
    end

    subgraph "API Layer"
        APIGW["API Gateway<br/>(Azure API Management - optional)"]
        API["FastAPI Backend<br/>(Azure Functions / Container Apps)"]
        MW["Middleware Stack"]
        MW_CORS["CORS"]
        MW_AUTH["JWT Auth"]
        MW_LOG["Correlation ID Logger"]
        MW_VAL["JSON Schema Validator"]
    end

    subgraph "Agent Orchestration Layer (Microsoft Agent Framework)"
        ORCH["Agent Orchestrator"]
        
        subgraph "Specialist Agents"
            CIA["Cultural Intelligence<br/>Agent"]
            UXA["UX Adaptation<br/>Agent"]
            CFA["Copy & Framing<br/>Agent"]
            CBA["Compliance & Bias<br/>Auditor Agent"]
            EXP["Experimentation<br/>Agent"]
        end
    end

    subgraph "AI Services"
        AOI["Azure OpenAI<br/>(via AI Foundry)"]
        PROMPTS["Agent System Prompts<br/>(Structured Output)"]
    end

    subgraph "Data Layer"
        PRIORS["Cultural Priors<br/>(JSON files)"]
        RULES["Dimension→UX<br/>Mapping Rules"]
        SCHEMAS["JSON Schemas<br/>(Validation)"]
        STORE["Variant Store<br/>(In-memory / Cosmos DB)"]
    end

    subgraph "Azure Platform Services"
        KV["Azure Key Vault"]
        AI_INS["Application Insights"]
        MI["Managed Identity"]
    end

    WEB -->|"POST /api/adapt<br/>GET /api/variants/:id<br/>POST /api/audit"| APIGW
    APIGW --> API
    API --> MW
    MW --> MW_CORS
    MW --> MW_AUTH
    MW --> MW_LOG
    MW --> MW_VAL

    API -->|"AdaptRequest"| ORCH
    
    ORCH -->|"1. Analyze culture"| CIA
    ORCH -->|"2. Adapt UX"| UXA
    ORCH -->|"3. Reframe copy"| CFA
    ORCH -->|"4. Audit compliance"| CBA
    ORCH -->|"5. Predict lift"| EXP

    CIA -->|"LLM Call"| AOI
    UXA -->|"LLM Call"| AOI
    CFA -->|"LLM Call"| AOI
    CBA -->|"LLM Call"| AOI
    EXP -->|"LLM Call"| AOI

    CIA -->|"Load priors"| PRIORS
    UXA -->|"Load rules"| RULES
    CBA -->|"Validate output"| SCHEMAS
    API -->|"Store/retrieve"| STORE

    API -->|"Secrets"| KV
    API -->|"Telemetry"| AI_INS
    KV -->|"Access via"| MI
```

## Agent Pipeline Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Orchestrator
    participant CulturalIntel as Cultural Intelligence
    participant UXAdapt as UX Adaptation
    participant CopyFrame as Copy & Framing
    participant Compliance as Compliance Auditor
    participant Experiment as Experimentation

    Client->>API: POST /api/adapt
    API->>API: Validate request (JSON Schema)
    API->>API: Generate correlation_id
    API->>Orchestrator: AdaptRequest + correlation_id
    
    Orchestrator->>CulturalIntel: Analyze region + product category
    CulturalIntel->>CulturalIntel: Load cultural priors
    CulturalIntel->>CulturalIntel: Apply dimension overrides
    CulturalIntel-->>Orchestrator: CulturalBehaviorProfile
    
    Orchestrator->>UXAdapt: Profile + StorefrontBaseSpec
    UXAdapt->>UXAdapt: Apply dimension→UX mapping rules
    UXAdapt-->>Orchestrator: Adapted flow + modules
    
    Orchestrator->>CopyFrame: Profile + UX adaptations
    CopyFrame-->>Orchestrator: Copy variants + rationale
    
    Orchestrator->>Compliance: Complete variant data
    Compliance->>Compliance: Check for bias/stereotypes
    Compliance->>Compliance: Verify dimension justifications
    Compliance-->>Orchestrator: audit_score + risk_flags
    
    Orchestrator->>Experiment: Complete variant + audit
    Experiment-->>Orchestrator: predicted_lift + A/B plan
    
    Orchestrator-->>API: VariantSpec
    API->>API: Store variant
    API-->>Client: VariantSpec + variant_id
```

## Component Details

### Frontend (Next.js)
- **Variant Switcher**: Side-by-side comparison of base vs adapted variants
- **Dimension Overrides**: Slider controls for manual dimension adjustment
- **Audit Dashboard**: Visual display of compliance scores and risk flags
- **Responsible AI Page**: Transparency, limitations, human-in-the-loop controls

### API Layer (FastAPI)
- **REST Endpoints**: `/api/adapt`, `/api/variants/:id`, `/api/audit`
- **JSON Schema Validation**: All inputs/outputs validated against schemas
- **Correlation IDs**: Every request gets a unique trace ID
- **Error Handling**: Safe defaults, structured error responses

### Agent Orchestrator
- **Sequential Pipeline**: Cultural → UX → Copy → Compliance → Experimentation
- **Structured Output**: Each agent returns JSON with `rationale` field
- **Tool Calls**: Agents can invoke cultural priors and mapping rules as tools

### Azure Services
- **Azure OpenAI**: GPT-4o for agent inference
- **Key Vault**: Secrets management with Managed Identity access
- **Application Insights**: Distributed tracing with correlation IDs
- **Static Web Apps**: Frontend hosting with CI/CD

## Generating Architecture Diagram as PNG

To export the Mermaid diagram as PNG:

1. **VS Code**: Install "Markdown Preview Mermaid Support" extension
2. **CLI**: Use `mmdc` (Mermaid CLI):
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   mmdc -i docs/architecture.md -o docs/architecture.png -t dark
   ```
3. **Online**: Paste the Mermaid code at [mermaid.live](https://mermaid.live)
