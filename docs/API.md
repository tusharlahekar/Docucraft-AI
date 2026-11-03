# REST API & Streaming Specifications

## Base URL
`/api/v1`

## 1. Authentication (`/api/v1/auth`)
- `POST /register`: Register user `{ email, password, full_name }` -> `{ user, access_token }`
- `POST /login`: Authenticate `{ email, password }` -> `{ user, access_token }`
- `GET /me`: Current user session and profile

## 2. Conversations (`/api/v1/conversations`)
- `GET /`: List user's conversations
- `POST /`: Create a new conversation `{ title?: string }`
- `GET /{id}`: Get conversation details, message history, and attached documents
- `PATCH /{id}`: Rename conversation `{ title: string }`
- `DELETE /{id}`: Delete conversation and associated logs

## 3. Chat & Multi-Agent Execution (`/api/v1/chat`)
- `POST /{conversation_id}/send`: Send message with optional file attachment IDs
  - Returns Server-Sent Events (SSE) or JSON response
  - Streams tokens, agent status transitions (`Supervisor`, `RAG`, `Research`, `Document Editing`), and emits citations & download payloads

## 4. Document Ingestion & Analysis (`/api/v1/documents`)
- `POST /upload`: Upload DOCX, PPTX, XLSX, or PDF file (multipart/form-data)
  - Saves file securely
  - Extracts text and full structural metadata (headings, tables, slides, shapes, fonts, colors)
  - Generates chunks and embeds them into ChromaDB
- `GET /`: List all uploaded documents for current user
- `GET /{id}`: Get document metadata, preview text, and structure breakdown
- `GET /{id}/download`: Download original file

## 5. Document Generation & Editing (`/api/v1/generation`)
- `POST /generate`: Request brand new DOCX, PPTX, or XLSX `{ file_type, prompt, options }`
- `POST /edit`: Request targeted edit on existing uploaded document `{ document_id, instructions }`
  - Performs format-preserving modifications
  - Produces comparison diff (added, deleted, modified)
  - Generates new downloadable artifact
- `GET /{id}/download`: Download generated or revised document
- `GET /{id}/diff`: Inspect structural differences between original and revised document

## 6. Web Research (`/api/v1/research`)
- `POST /search`: Free DuckDuckGo / SearXNG search `{ query, max_results?: 5 }` -> `{ results: [{ title, url, snippet }] }`

## 7. Dashboard & Analytics (`/api/v1/dashboard`)
- `GET /stats`: Aggregated summary:
  - Total conversations
  - Total uploaded documents
  - Total generated documents
  - Recent activity feed
  - System health (Ollama status, ChromaDB status, Database status)
