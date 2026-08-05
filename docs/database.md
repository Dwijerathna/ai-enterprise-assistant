# Database Design


## Database

PostgreSQL


# Entity Relationship Overview


Organization

|

Users

|

Documents

|

Document Chunks

|

Conversations

|

Messages



# Tables


## Organizations


Purpose:

Support multiple companies/workspaces.


Fields:

id

name

created_at



---


## Users


Purpose:

System users.


Fields:

id

organization_id
department_id

name

email

password_hash

role

created_at




---


## Conversations Table


Purpose:

Stores AI chat sessions.


Fields:


| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| organization_id | UUID | Tenant ownership |
| user_id | UUID | Conversation owner |
| title | VARCHAR | Conversation title |
| created_at | TIMESTAMP | Creation date |



Indexes:


- organization_id
- user_id



# Document Processing Lifecycle


The document ingestion pipeline is asynchronous and tracks progress using processing_status.


## Document Status Flow


pending

↓

uploading

↓

extracting

↓

cleaning

↓

chunking

↓

embedding

↓

indexing

↓

ready


If any stage fails:

↓

failed


## Status Definitions


| Status | Description |
|---|---|
| pending | Document record created but processing has not started |
| uploading | File upload is in progress |
| extracting | Text extraction is running |
| cleaning | Extracted text is cleaned |
| chunking | Text is divided into semantic chunks |
| embedding | Vector embeddings are generated |
| indexing | Chunks are stored in Qdrant |
| ready | Document is available for retrieval |
| failed | Processing failed |

## Tracking Fields


Documents table maintains:

- processing_status
- processing_started_at
- processing_completed_at
- error_message

# Document Chunk Metadata


Each document chunk stored in Qdrant maintains metadata required for retrieval and citations.


Metadata Fields:


document_id

organization_id

chunk_id

page_number

section_title

document_name



Purpose:


- Permission filtering
- Source citation
- Document traceability
- Retrieval debugging

## Messages Table


Purpose:

Stores individual messages exchanged between users and the AI assistant.


Fields:


| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| organization_id | UUID | Tenant ownership |
| conversation_id | UUID | Related conversation |
| document_id | UUID | Source document reference (nullable) |
| role | ENUM | user, assistant, system |
| content | TEXT | Message content |
| timestamp | TIMESTAMP | Creation time |



Indexes:


- organization_id
- conversation_id
- document_id

## Organization Table


Fields:


| Field | Type |
|-|-|
| id | UUID |
| name | VARCHAR |
| qdrant_collection_name | VARCHAR |
| created_at | TIMESTAMP |

## Documents Table


Fields:


| Field | Type | Description |
|-|-|-|
| id | UUID | Primary key |
| organization_id | UUID | Tenant ownership |
| uploaded_by | UUID | User who uploaded |
| department_id | UUID | Document department ownership |
| filename | VARCHAR | File name |
| file_type | VARCHAR | Document type |
| processing_status | ENUM | Processing state |
| employee_visible | BOOLEAN | Employee visibility control |
| created_at | TIMESTAMP | Creation date |
# Departments Table


Purpose:

Groups users and documents inside an organization.


Fields:


| Field | Type |
|-|-|
| id | UUID |
| organization_id | UUID |
| name | VARCHAR |
| created_at | TIMESTAMP |



Relationship:


Organization

↓

Departments

↓

Users

↓

Documents