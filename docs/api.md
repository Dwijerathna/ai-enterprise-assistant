# API Specification


Base URL:

/api/v1



# Authentication


## Register User


POST

/auth/register


Request:

{
name,
email,
password
}


Response:

{
message,
user_id
}



---


## Login

POST /auth/login

POST /auth/refresh

POST /auth/logout



Returns:

JWT Token



---


# Document API


## Upload Document


POST

/documents/upload


Purpose:

Supported File Types:


- PDF
- DOCX
- TXT
- CSV



## Get Documents


GET

/documents



Returns:

User accessible documents.



---


# AI Chat API


POST

/chat


Request:


{
message,
conversation_id
}



Response:


{
answer,
sources
}



---


# Health Check


GET

/health


Purpose:

System monitoring.
# Document Processing API


## Upload Document


Endpoint:


POST /api/v1/documents/upload



Purpose:


Uploads enterprise documents and starts the AI ingestion pipeline asynchronously.



Response:


{
    "document_id": "12345",
    "status": "processing",
    "message": "Document processing started"
}



---


## Check Document Processing Status


Endpoint:


GET /api/v1/documents/{document_id}/status



Purpose:


Returns the current processing state of an uploaded document.



Response:


{
    "document_id": "12345",
    "status": "ready",
    "progress": 100
}



Possible Status Values:


- pending
- processing
- ready
- failed

# Organization Registration Flow


## Register Organization


POST /auth/register


Purpose:

Creates a new organization and the first administrator account.


Request:


{
"name":"John",
"email":"john@company.com",
"password":"password",
"organization_name":"ABC Company"
}



Process:


1. Create Organization

2. Create User

3. Assign Admin Role

4. Link User to Organization

# Streaming Authentication


The frontend uses Fetch API streaming instead of native EventSource.


Reason:


Native EventSource does not support custom Authorization headers.


Authentication:


Authorization:

Bearer JWT Token



Response:


text/event-stream

# API Pagination Standard


All list endpoints must support pagination.


Example:


GET /documents?page=1&limit=20



Response:


{
"data":[],
"page":1,
"limit":20,
"total":200
}

# Document Processing Progress API


## Get Processing Status


Endpoint:


GET /api/v1/documents/{document_id}/status



Purpose:


Returns the current AI ingestion stage of a document.



Response Example:


{
    "document_id":"12345",
    "status":"processing",
    "stage":"embedding_generation",
    "progress":70
}



Possible Stages:


- upload
- extraction
- cleaning
- chunking
- embedding
- indexing
- completed
- failed
# Organization Registration Flow


## Create Organization Account


Endpoint:


POST /auth/register



Purpose:


Creates a new organization and the first administrator account.



Request:


{
"name":"John Smith",
"email":"john@company.com",
"password":"password",
"organization_name":"ABC Company"
}



Process:


1. Create Organization record

2. Create User record

3. Assign Admin role

4. Link User to Organization



Response:


{
"user_id":"123",
"organization_id":"456",
"role":"ADMIN"
}

# Login Response


POST /auth/login



Response:


Access Token:

Returned in response body.


Refresh Token:

Stored in HttpOnly Secure Cookie.



Example Response:


{
"access_token":"jwt_token",
"token_type":"bearer"
}



Cookie:


refresh_token