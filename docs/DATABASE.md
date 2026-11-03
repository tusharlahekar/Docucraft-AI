# Database Architecture & Schema Specification

## 1. Engine & Strategy
- **Primary Engine**: PostgreSQL
- **Fallback / Embedded Engine**: SQLite (aiosqlite) with automated fallback if PostgreSQL connection string is unavailable or unreachable in a local dev test environment.
- **ORM / Migrations**: SQLAlchemy 2.0 (asyncio) + Alembic.

## 2. Entity Relationship Diagram (Conceptual)
```
[User] 1 --- * [Conversation] 1 --- * [Message]
  |                   |                   |
  |                   +--- * [UploadedDoc]|
  |                                       |
  +--- * [UploadedDocument] 1 --- 1 [DocumentMetadata]
  |           |
  |           +--- * [DocumentChunk]
  |           |
  |           +--- * [DocumentVersion]
  |
  +--- * [GeneratedDocument]
  |
  +--- * [AgentExecutionLog]
  |
  +--- * [ResearchSource]
```

## 3. Schema Definitions

### 1. `users`
- `id` (VARCHAR / UUID, Primary Key)
- `email` (VARCHAR(255), Unique, Indexed)
- `hashed_password` (VARCHAR(255))
- `full_name` (VARCHAR(255))
- `is_active` (BOOLEAN, default TRUE)
- `created_at` (TIMESTAMP WITH TIME ZONE, default UTC NOW)
- `updated_at` (TIMESTAMP WITH TIME ZONE)

### 2. `conversations`
- `id` (VARCHAR / UUID, Primary Key)
- `user_id` (VARCHAR / UUID, Foreign Key -> `users.id`, Indexed)
- `title` (VARCHAR(255))
- `created_at` (TIMESTAMP WITH TIME ZONE, default UTC NOW)
- `updated_at` (TIMESTAMP WITH TIME ZONE)

### 3. `messages`
- `id` (VARCHAR / UUID, Primary Key)
- `conversation_id` (VARCHAR / UUID, Foreign Key -> `conversations.id`, Indexed)
- `sender` (VARCHAR(20): 'user' | 'assistant' | 'system')
- `content` (TEXT)
- `citations` (JSONB / JSON: array of {title, url, snippet})
- `attached_doc_ids` (JSONB / JSON: array of doc IDs)
- `generated_doc_ids` (JSONB / JSON: array of generated doc IDs)
- `agent_logs` (JSONB / JSON: execution steps recorded by LangGraph)
- `created_at` (TIMESTAMP WITH TIME ZONE, default UTC NOW)

### 4. `uploaded_documents`
- `id` (VARCHAR / UUID, Primary Key)
- `user_id` (VARCHAR / UUID, Foreign Key -> `users.id`, Indexed)
- `conversation_id` (VARCHAR / UUID, Nullable, Foreign Key -> `conversations.id`)
- `filename` (VARCHAR(255))
- `file_type` (VARCHAR(20): 'docx' | 'pptx' | 'xlsx' | 'pdf')
- `file_size` (BIGINT)
- `storage_path` (VARCHAR(500))
- `parsed_status` (VARCHAR(20): 'pending' | 'processing' | 'completed' | 'failed')
- `created_at` (TIMESTAMP WITH TIME ZONE, default UTC NOW)

### 5. `document_metadata`
- `id` (VARCHAR / UUID, Primary Key)
- `document_id` (VARCHAR / UUID, Unique, Foreign Key -> `uploaded_documents.id`)
- `structure_summary` (JSONB / JSON: headings, page_count, slides_count, sheets, tables, fonts, colors)
- `created_at` (TIMESTAMP WITH TIME ZONE, default UTC NOW)

### 6. `document_chunks`
- `id` (VARCHAR / UUID, Primary Key)
- `document_id` (VARCHAR / UUID, Foreign Key -> `uploaded_documents.id`, Indexed)
- `user_id` (VARCHAR / UUID, Foreign Key -> `users.id`, Indexed)
- `chunk_index` (INTEGER)
- `content` (TEXT)
- `metadata_json` (JSONB / JSON: page, section, heading, slide_no, sheet_name)
- `chroma_id` (VARCHAR(255), Indexed)
- `created_at` (TIMESTAMP WITH TIME ZONE, default UTC NOW)

### 7. `generated_documents`
- `id` (VARCHAR / UUID, Primary Key)
- `user_id` (VARCHAR / UUID, Foreign Key -> `users.id`, Indexed)
- `conversation_id` (VARCHAR / UUID, Foreign Key -> `conversations.id`, Indexed)
- `source_document_id` (VARCHAR / UUID, Nullable, Foreign Key -> `uploaded_documents.id`)
- `filename` (VARCHAR(255))
- `file_type` (VARCHAR(20): 'docx' | 'pptx' | 'xlsx')
- `file_size` (BIGINT)
- `storage_path` (VARCHAR(500))
- `generation_type` (VARCHAR(50): 'created_from_scratch' | 'edited_from_source')
- `diff_summary` (JSONB / JSON: added, modified, deleted sections)
- `created_at` (TIMESTAMP WITH TIME ZONE, default UTC NOW)

### 8. `document_versions`
- `id` (VARCHAR / UUID, Primary Key)
- `document_id` (VARCHAR / UUID, Foreign Key -> `uploaded_documents.id`, Indexed)
- `version_number` (INTEGER)
- `storage_path` (VARCHAR(500))
- `change_description` (TEXT)
- `created_at` (TIMESTAMP WITH TIME ZONE, default UTC NOW)

### 9. `research_sources`
- `id` (VARCHAR / UUID, Primary Key)
- `conversation_id` (VARCHAR / UUID, Foreign Key -> `conversations.id`, Indexed)
- `query` (TEXT)
- `title` (VARCHAR(500))
- `url` (VARCHAR(1000))
- `snippet` (TEXT)
- `retrieval_date` (TIMESTAMP WITH TIME ZONE, default UTC NOW)

### 10. `agent_execution_logs`
- `id` (VARCHAR / UUID, Primary Key)
- `conversation_id` (VARCHAR / UUID, Foreign Key -> `conversations.id`, Indexed)
- `agent_name` (VARCHAR(100))
- `step_name` (VARCHAR(100))
- `input_state_summary` (JSONB / JSON)
- `output_state_summary` (JSONB / JSON)
- `execution_time_ms` (INTEGER)
- `created_at` (TIMESTAMP WITH TIME ZONE, default UTC NOW)
