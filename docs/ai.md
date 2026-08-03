# AI System Design


# AI Components


## Large Language Model


Technology:

Ollama


Models:

- Llama
- Gemma
- Mistral



# RAG Pipeline


## Document Processing


Steps:


Upload document

↓

Extract text

↓

Clean text

↓

Chunk content

↓

Generate embeddings

↓

Store vectors in Qdrant



# Retrieval Process


User Question

↓

Convert question to embedding

↓

Search Qdrant

↓

Retrieve relevant chunks

↓

Send context to LLM

↓

Generate answer



# Embedding Model


Purpose:

Convert text into numerical vectors.



# Vector Database


Technology:

Qdrant



Stores:

- Document vectors
- Metadata
- Permissions


# Future AI Features


- Forecasting
- Recommendation engine
- Automated reports
- AI agents
# Vector Database Isolation


Qdrant collections are separated by organization.


Example:

organization_id:

company_a


Collection:

company_a_documents


Benefits:

- Prevent cross-company retrieval
- Reduce security risk
- Simplify filtering logic
# Local Model Limitation


The system uses local LLM inference through Ollama.


Advantages:

- Zero API cost
- Data privacy


Limitations:

- Limited concurrent requests
- Hardware dependent
- Higher latency


Mitigation:

- Request queue
- Rate limiting
- Streaming responses
- Model optimization

## Document Chunking Strategy

The system uses semantic chunking instead of fixed character splitting.

Chunk boundaries are created based on:

- Paragraph structure
- Sentence boundaries
- Document headings

Goal:

Maintain contextual meaning during retrieval.

# Embedding Model Strategy


## Dedicated Embedding Model


The system separates embedding generation from language generation by using a dedicated embedding model optimized for semantic search.


The Large Language Model (LLM) is responsible for generating responses, while the embedding model is responsible for converting documents and queries into numerical vector representations.


## Embedding Model


Primary Model:

nomic-embed-text


Purpose:

- Generate embeddings for uploaded enterprise documents
- Generate embeddings for user queries
- Improve semantic retrieval accuracy
- Reduce dependency on larger LLM models for search operations


## Embedding Pipeline


Document Upload

↓

Text Extraction

↓

Semantic Chunking

↓

Embedding Generation

↓

Store Embeddings in Qdrant


## Benefits


- Improved RAG retrieval accuracy
- Faster vector generation
- Reduced computational requirements
- Better separation between retrieval and generation tasks
# Streaming AI Response Architecture


## Server-Sent Events (SSE)


The system uses Server-Sent Events (SSE) to stream AI-generated responses from the backend to the frontend in real time.


## Response Flow


User Question

↓

FastAPI API Layer

↓

Permission Validation

↓

RAG Retrieval

↓

Ollama LLM Processing

↓

Token Streaming

↓

Next.js Chat Interface



## Benefits


- Reduces perceived response time
- Provides ChatGPT-like interaction
- Improves experience with slower local models
- Allows users to see responses while generation continues



## Implementation


Backend:


FastAPI StreamingResponse



Frontend:


Next.js streaming client



Response Format:


text/event-stream

# Document Chunking Configuration


The system uses semantic chunking with maximum size limits.


Strategy:


Primary:

- Paragraph boundaries
- Sentence boundaries
- Document headings


Secondary:

Maximum chunk size protection


Purpose:

Prevent oversized chunks from exceeding LLM context limits.

# Hybrid Search Retrieval Architecture


## Overview


The RAG system combines semantic vector search with keyword-based search to improve document retrieval accuracy.


Pure vector search performs well for understanding meaning but may struggle with exact matches such as:


- Invoice numbers
- Employee IDs
- Policy codes
- Contract references


The system implements hybrid retrieval by combining:


1. Dense Vector Search

2. Sparse Keyword Search



## Retrieval Flow


User Query

↓

Query Processing

↓

Dense Embedding Generation

↓

Qdrant Vector Search


AND


Keyword Search (Sparse Retrieval)

↓

Result Combination

↓

Reciprocal Rank Fusion (RRF)

↓

Relevant Context Selection

↓

LLM Response Generation



## Benefits


- Improved retrieval accuracy
- Better handling of exact keywords
- Reduced irrelevant context retrieval
- Improved enterprise document search reliability

# AI Response Source Citation


## Overview


The RAG system provides references to the original document sources used during AI response generation.


The goal is to improve:


- User trust
- AI transparency
- Enterprise adoption



## Citation Flow


User Question

↓

Permission Validation

↓

Document Retrieval

↓

Relevant Chunks Selected

↓

LLM Generates Response

↓

Attach Source Metadata

↓

Display Answer With References



## Source Metadata Stored


Each retrieved chunk maintains:


- Document name
- Page number
- Section heading
- Chunk identifier
Qdrant Collection Strategy


Each organization has an isolated Qdrant collection.


Example:


Organization:

ABC Company


Collection:

abc_company_documents



All document chunks belonging to that organization are stored inside that collection.


Benefits:

- Prevent cross-tenant retrieval
- Simplify permission filtering
- Improve security isolation



## Example Response


AI Answer:


Employees receive 25 days of annual leave.


Sources:


Employee_Policy.pdf

Page: 4

Section: Leave Policy



## Benefits


- Reduces hallucination concerns
- Improves answer verification
- Builds user confidence
- Supports enterprise compliance requirements