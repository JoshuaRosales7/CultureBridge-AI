# Threat Model

## System Overview

CultureBridge AI is a web application with:
- Public-facing Next.js frontend
- FastAPI backend processing culturally-adaptive requests
- Azure OpenAI integration for LLM inference
- Multi-agent orchestration pipeline

## Assets to Protect

| Asset | Classification | Owner |
|-------|---------------|-------|
| Azure OpenAI API keys | Secret | Platform team |
| JWT signing secret | Secret | Platform team |
| Cultural behavior profiles (synthetic) | Internal | Data team |
| Generated variant specs | Internal | Application |
| Application source code | Public (open source) | All contributors |
| User session data | Sensitive | Application |

## Threat Analysis (STRIDE)

### Spoofing
| Threat | Risk | Mitigation |
|--------|------|------------|
| Attacker impersonates legitimate API user | Medium | JWT bearer token authentication on all API endpoints |
| Attacker accesses Azure resources | High | Azure Managed Identity; no stored credentials |
| Token theft/replay | Medium | Short token expiry; HTTPS-only; secure cookie flags |

### Tampering
| Threat | Risk | Mitigation |
|--------|------|------------|
| Modified API requests bypass validation | Medium | JSON Schema validation on all inputs |
| Tampered cultural priors produce biased output | High | Data integrity checks; auditor agent validates outputs |
| Modified agent prompts produce harmful content | High | System prompts stored server-side; not user-modifiable |

### Repudiation
| Threat | Risk | Mitigation |
|--------|------|------------|
| Denial of API usage | Low | Correlation ID logging via Application Insights |
| Denial of variant generation | Low | Full request/response logging with trace IDs |

### Information Disclosure
| Threat | Risk | Mitigation |
|--------|------|------------|
| API key exposure in client code | Critical | Keys stored in Azure Key Vault; never in frontend |
| System prompt leakage via LLM responses | Medium | Structured output constraints; output post-processing |
| Error messages revealing internals | Medium | Generic error responses in production; detailed logs server-side only |

### Denial of Service
| Threat | Risk | Mitigation |
|--------|------|------------|
| API flood consuming Azure OpenAI quota | High | Rate limiting; per-user quotas; Azure API Management |
| Large payload submission | Medium | Request size limits; input validation |
| Recursive/malicious agent calls | Medium | Agent execution timeout limits; call depth limits |

### Elevation of Privilege
| Threat | Risk | Mitigation |
|--------|------|------------|
| Prompt injection via user input | High | Input sanitization; structured tool calls; no raw user input in system prompts |
| Unauthorized access to admin endpoints | Medium | Role-based access control; JWT claims validation |

## AI-Specific Threats

### Prompt Injection
- **Risk**: User-crafted inputs (e.g., override_dimensions descriptions) could attempt to modify agent system prompts
- **Mitigation**: 
  - Override dimensions accept only numeric values (0-100)
  - No free-text user input is concatenated into system prompts
  - Agent outputs are validated against JSON schemas before returning to user

### Bias Amplification
- **Risk**: LLM may amplify cultural stereotypes despite explicit instructions
- **Mitigation**:
  - Compliance & Bias Auditor agent reviews all outputs
  - Dimension-based justification required (not stereotype-based)
  - Human-in-the-loop override capability
  - Regular audits of generated content

### Hallucinated Data
- **Risk**: LLM may generate fabricated evidence sources or statistics
- **Mitigation**:
  - Evidence sources are drawn from pre-defined cultural priors data
  - Predicted lift uses explicit heuristic formula, not LLM-generated numbers
  - All predictions clearly marked as "simulated/predicted"

## Network Diagram

```
Internet → Azure Front Door (optional)
         → Azure Static Web Apps (frontend)
         → Azure Functions (API)
           ├── Azure Key Vault (secrets)
           ├── Azure OpenAI (LLM inference)
           └── Application Insights (logging)
```

## Security Controls Summary

| Control | Implementation |
|---------|---------------|
| Authentication | JWT bearer tokens |
| Authorization | Role-based claims |
| Secrets Management | Azure Key Vault + Managed Identity |
| Input Validation | JSON Schema on all endpoints |
| Output Validation | Schema validation + bias auditor |
| Encryption in Transit | TLS 1.2+ everywhere |
| Logging & Monitoring | Application Insights with correlation IDs |
| Rate Limiting | Per-user request limits |
| Dependency Management | Dependabot + regular audits |
| CORS | Restricted to known origins |
