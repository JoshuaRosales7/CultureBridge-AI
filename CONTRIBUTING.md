# Contributing to CultureBridge AI

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## 🏗️ Development Setup

### Prerequisites

- Node.js 18+ and pnpm 8+
- Python 3.11+
- Azure CLI (for deployment testing)
- VS Code with GitHub Copilot extension (recommended)

### Getting Started

1. **Fork the repository** and clone your fork
2. **Install dependencies**:
   ```bash
   pnpm install
   cd apps/api && pip install -r requirements.txt
   ```
3. **Copy environment variables**:
   ```bash
   cp .env.example .env
   # Fill in your Azure OpenAI credentials
   ```
4. **Start development servers**:
   ```bash
   pnpm dev          # Frontend on :3000
   cd apps/api && uvicorn main:app --reload --port 8000
   ```

## 📋 Code Standards

### Python (Backend / Agents)

- **Formatter**: `black` (line length 100)
- **Linter**: `ruff`
- **Type hints**: Required for all function signatures
- **Docstrings**: Required for public functions and classes

### TypeScript (Frontend)

- **Formatter**: Prettier
- **Linter**: ESLint with Next.js config
- **Types**: Strict mode enabled, no `any` types

### General

- All API responses must include `correlation_id`
- All agent outputs must include `rationale` field
- No hardcoded secrets — use environment variables
- Cultural adaptations must reference behavioral dimensions, never stereotypes

## 🧪 Testing

```bash
# Backend tests
cd apps/api && python -m pytest tests/ -v

# Frontend tests
pnpm test
```

### Test Requirements

- New mapping rules require corresponding unit tests
- Schema changes require validation tests
- Agent prompt changes require output format tests

## 🔀 Pull Request Process

1. Create a feature branch: `feature/your-feature-name`
2. Make your changes with clear, atomic commits
3. Ensure all tests pass
4. Update documentation if needed
5. Submit a PR with:
   - Clear description of changes
   - Link to related issue (if any)
   - Screenshots for UI changes
   - Test results

## ⚠️ Cultural Sensitivity Guidelines

This project deals with cultural behavioral differences. When contributing:

- **DO** reference behavioral dimensions (e.g., "high uncertainty avoidance")
- **DO NOT** use essentializing statements ("People in X always...")
- **DO** provide rationale grounded in research frameworks
- **DO NOT** use color/visual stereotypes (e.g., "Japan = red")
- **DO** flag potential bias in your own contributions
- **DO** consider that cultural profiles are generalizations with individual variance

## 📝 Commit Message Format

```
type(scope): description

# Examples:
feat(agents): add dimension override support to Cultural Intelligence Agent
fix(api): handle missing country_code in adapt endpoint
docs(cultural-model): clarify uncertainty avoidance mapping rules
test(schemas): add validation tests for VariantSpec
```

## 🐛 Reporting Issues

Use GitHub Issues with the appropriate template:
- **Bug Report**: Something isn't working
- **Feature Request**: Suggest an improvement
- **Cultural Concern**: Flag a potential bias or stereotype issue

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.
