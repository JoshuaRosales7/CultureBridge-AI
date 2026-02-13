# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | ✅ Yes             |
| < 1.0   | ❌ No              |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **DO NOT** open a public GitHub issue
2. **Email**: security@your-domain.com (replace with actual contact)
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if any)

We will acknowledge receipt within **48 hours** and provide an initial assessment within **5 business days**.

## Security Measures

### Authentication & Authorization
- API endpoints protected with JWT bearer tokens
- Azure Managed Identity for service-to-service authentication
- No API keys stored in code or configuration files

### Secrets Management
- All secrets stored in **Azure Key Vault**
- Environment variables used for local development (via `.env` files, gitignored)
- Managed Identity used to access Key Vault in production

### Data Protection
- No PII stored in cultural behavior profiles
- All API communication over HTTPS/TLS 1.2+
- Input validation on all API endpoints using JSON Schema
- Output sanitization to prevent XSS

### Infrastructure Security
- Azure resources deployed with least-privilege access
- Network isolation via Virtual Networks where applicable
- Regular dependency updates via Dependabot
- CORS restricted to known origins

### AI/LLM Security
- Prompt injection mitigations via input validation and structured outputs
- No user input directly concatenated into system prompts
- Rate limiting on AI-powered endpoints
- Content filtering enabled on Azure OpenAI

## Security Checklist for Contributors

- [ ] No secrets or API keys in committed code
- [ ] Input validation for all new API endpoints
- [ ] Content sanitization for user-facing outputs
- [ ] Dependency versions pinned and audited
- [ ] New Azure resources follow least-privilege principle

## Dependencies

We regularly audit our dependencies using:
- `pip audit` for Python packages
- `pnpm audit` for Node.js packages
- GitHub Dependabot for automated updates
