# Development Guide

## Project Development Rules

This document defines the development standards, workflow, and responsibilities for the Enterprise AI Assistant project.

---

# 1. Development Philosophy

The project follows:

- Clean Architecture principles
- Modular development
- Security-first design
- Documentation-driven development
- Testable and maintainable code

The architecture should support future AI expansion without requiring major restructuring.

---

# 2. Technology Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

## Frontend

- Next.js
- TypeScript
- Tailwind CSS

## AI Layer

- Ollama
- Qdrant
- Local embedding models
- RAG pipeline

---

# 3. Backend Structure Rules

The backend follows:

API → Services → Repositories → Database


## api/

Purpose:
Contains HTTP endpoints.

Responsibilities:
- Request handling
- Response formatting
- Input validation

Should NOT contain:
- Database queries
- Business logic


---

## services/

Purpose:
Contains business logic.

Responsibilities:
- User operations
- Document workflows
- AI orchestration


---

## repositories/

Purpose:
Database abstraction layer.

Responsibilities:
- Database queries
- Tenant filtering
- Data access rules


All organization-scoped queries MUST enforce organization isolation here.

---

## models/

Purpose:
SQLAlchemy database models.

---

## schemas/

Purpose:
Pydantic request and response models.

---

## security/

Purpose:
Authentication and authorization logic.

Contains:
- JWT handling
- Password hashing
- RBAC permissions


---

# 4. Multi-Tenant Security Rule

Every organization-owned resource MUST enforce:

organization_id filtering.

No repository method should return data without tenant validation.

---

# 5. Git Workflow

Branches:

main
- Production-ready code

develop
- Integration branch

feature/*
- Individual features


Example:

feature/authentication

feature/document-upload

feature/rag-pipeline


---

# 6. Code Quality Rules

Every feature should include:

- Clear naming
- Error handling
- Documentation
- Testing where applicable


Avoid:

- Duplicate logic
- Hardcoded values
- Direct database access from API routes

---

# 7. AI Development Workflow

AI tools have assigned responsibilities:

## Claude

Role:
Architecture and security reviewer.

Used for:
- Design reviews
- Security audits
- Code reviews


## Gemini

Role:
AI strategy and innovation reviewer.

Used for:
- RAG improvements
- AI features
- Optimization ideas


## Cursor

Role:
Primary implementation assistant.

Used for:
- Writing code
- Refactoring
- Debugging


---

# 8. Development Process

Every feature follows:

1. Requirement analysis
2. Architecture review
3. Implementation
4. Testing
5. Code review
6. Documentation update


---

# 9. Definition of Done

A feature is complete only when:

- Code works
- Security requirements are satisfied
- Documentation is updated
- No architecture rules are violated
