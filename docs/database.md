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


## Documents


Purpose:

Store uploaded enterprise documents.


Fields:


id

organization_id

filename

file_type



chunk_count



created_at
processing_status

values:

pending
processing
ready
failed



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


## Messages


Purpose:

Store chat messages.


Fields:

id

conversation_id

role

content

timestamp

INDEX organization_id

INDEX user_id

INDEX conversation_id

INDEX document_id
# Document Processing Lifecycle


## Processing Status Management


The document ingestion process is asynchronous and uses status tracking to monitor the progress of uploaded documents.


## Document Status Flow


pending

↓

processing

↓

ready

↓

failed



## Status Definitions


### Pending


The document has been uploaded but processing has not started.


### Processing


The system is currently performing:


- Text extraction
- Content cleaning
- Semantic chunking
- Embedding generation
- Vector storage


### Ready


The document has been successfully processed and is available for AI retrieval.


### Failed


The document processing pipeline failed due to:

- Unsupported file format
- Extraction errors
- Embedding generation errors
- Storage failures



## Database Field Addition


Documents Table:


processing_status


Possible values:


- pending
- processing
- ready
- failed

## Tenant Isolation Fields


All organization-owned tables must contain organization_id.


Required tables:


Users

- organization_id


Documents

- organization_id


Conversations

- organization_id


Messages

- organization_id



Reason:

Direct organization filtering prevents accidental cross-tenant data exposure.

# Document Processing Tracking


The document table maintains processing information to support asynchronous ingestion.


Additional Fields:


processing_status

Possible values:

- pending
- processing
- ready
- failed


processing_started_at

Stores processing start time.



processing_completed_at

Stores successful completion time.



error_message

Stores failure details when processing fails.

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