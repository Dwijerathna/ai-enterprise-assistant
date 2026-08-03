# Project Context

## Project Name

AI Enterprise Intelligence Workspace


---

# Project Vision

A zero-cost AI-powered enterprise assistant that helps organizations analyze data, search documents, automate workflows, and generate intelligent recommendations.


---

# Main Objective

Build a production-level AI application using modern software engineering practices and open-source AI technologies.


---

# Technology Stack

## Frontend

Framework:
Next.js

Language:
TypeScript

Styling:
Tailwind CSS


## Backend

Framework:
FastAPI

Language:
Python


## Database

PostgreSQL


## AI Stack

LLM:
Ollama Local Models

Models:
Llama 3 / Gemma / Mistral


Vector Database:
Qdrant


Machine Learning:

Scikit-learn
TensorFlow


---

# System Architecture

Frontend:

Next.js application


Backend:

FastAPI REST API


AI Layer:

RAG pipeline
Document processing
Recommendation engine


Database:

PostgreSQL


Architecture flow:

User

↓

Next.js Frontend

↓

FastAPI Backend

↓

AI Engine

↓

Database / Vector Database


---

# Current Features

Completed:

- Project setup
- Initial architecture


In Progress:

- Authentication system


Pending:

- RAG implementation
- AI assistant
- Analytics dashboard


---

# Database Design

Main entities:

Users

Documents

Conversations

AI Responses

Reports


---

# Coding Rules

Follow:

- Clean architecture
- SOLID principles
- REST API standards
- Meaningful variable names
- Proper error handling
- Write comments for complex logic


---

# Development Rules

Before creating new features:

1. Check existing architecture
2. Avoid duplicate functionality
3. Update documentation
4. Write tests


---

# Current Problems

None


---

# Important Decisions

Decision 1:

Use local AI models instead of paid APIs to maintain zero-cost development.


Decision 2:

Use RAG instead of fine-tuning because it is cheaper and easier to maintain.


---

# AI Assistant Instructions

When helping with this project:

- Follow existing architecture
- Do not introduce unnecessary frameworks
- Explain design decisions
- Consider scalability and security
- Prefer free/open-source solutions
