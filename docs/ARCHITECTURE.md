# System Architecture Plan: AI Chatbot & Document Generation Platform

## 1. Overview & Core Philosophy
The platform is an enterprise-grade, 100% free and open-source, locally run AI Document Assistant and Multi-Agent Generation/Editing Platform. It enables users to converse with an AI chatbot, upload documents (DOCX, PPTX, XLSX, PDF), perform semantic search (RAG) and web research, generate professional office documents from scratch, and crucially, **edit existing documents while preserving their formatting, styles, slide masters, themes, and spreadsheet formulas**.

## 2. Technology Stack (Zero-Cost / FOSS Verification)
| Layer | Technology | Cost / License | Local Execution Details |
|---|---|---|---|
| **Frontend** | React 18 + TypeScript + Vite + Tailwind CSS | MIT | Single Page App on localhost:5173 |
| **Backend API** | FastAPI + Uvicorn + Pydantic v2 | MIT | High-performance async ASGI on localhost:8000 |
| **Multi-Agent AI** | LangGraph + LangChain | MIT | State-driven cyclic workflow graph |
| **Local LLM** | Ollama (Qwen2.5 / Llama 3.1) + Smart Fallback | FOSS / Free | Local Ollama HTTP daemon on `http://localhost:11434` with built-in heuristic/template-guided fallback |
| **Vector DB** | ChromaDB (embedded persistent) | Apache 2.0 | `./chroma_data` on disk, zero cloud dependency |
| **Embeddings** | HuggingFace MiniLM / OnnxRuntime local | Apache 2.0 | Runs on CPU, local vectors, no API keys |
| **Relational DB** | PostgreSQL (with auto SQLite aiosqlite fallback) | PostgreSQL / Public Domain | Full schema with ACID, migrations, foreign keys |
| **Word Engine** | python-docx + lxml OOXML DOM | BSD / BSD | Targeted XML-level and DOM run-level editing |
| **PowerPoint Engine** | python-pptx + shape tree manipulation | MIT | Preserves slide masters, layouts, placeholders |
| **Excel Engine** | openpyxl + XML style preservation | MIT | Formula preservation, cell style retention |
| **PDF & OCR** | PyMuPDF (fitz) + Tesseract fallback | AGPL / Apache 2.0 | Local text and structure extraction |
| **Web Research** | DuckDuckGo Search (`duckduckgo-search` primp) | MIT | Zero-cost web search with URL & title citations |

## 3. High-Level System Architecture

```
+---------------------------------------------------------------------------------------+
|                                Frontend (React + Vite)                                |
|  - Auth Pages (Login/Register)      - Dashboard (Metrics, Quick Actions, History)     |
|  - AI Chat Workspace (Streaming,    - Document Preview & Analysis Explorer            |
|    File Attachments, Sidebar)       - Side Panel (Agent Logs, Citations, Diffs)       |
+-------------------------------------------+-------------------------------------------+
                                            | REST API / Server-Sent Events (SSE)
+-------------------------------------------v-------------------------------------------+
|                               FastAPI Application Layer                               |
|  - Auth & Security (/api/auth)      - Conversations & Messages (/api/chat)            |
|  - Document Ingestion (/api/docs)   - Document Generation & Editing (/api/generation) |
|  - Web Research (/api/research)     - Health & System Metrics (/api/dashboard)        |
+-------------------------------------------+-------------------------------------------+
                                            |
         +----------------------------------+----------------------------------+
         |                                                                     |
+--------v-----------------------+                                   +---------v--------+
|      LangGraph Multi-Agent     |                                   | Storage & DB     |
|  - Supervisor Agent            |                                   | - PostgreSQL     |
|  - Document Understanding      |                                   |   (Users, Chats, |
|  - Web Research Agent          |                                   |    Docs, Logs)   |
|  - RAG Agent (ChromaDB)        |                                   | - ChromaDB       |
|  - Content Generation Agent    |                                   |   (Chunks &      |
|  - Document Editing Agent      |                                   |    Embeddings)   |
|  - Validation Agent            |                                   | - Storage Store  |
|  - Document Generation Agent   |                                   |   (DOCX/PPTX/    |
|  - Response Agent              |                                   |    XLSX/PDFs)    |
+--------------------------------+                                   +------------------+
```

## 4. LangGraph Multi-Agent Architecture

```
                                  +-------------------+
                                  |    User Request   |
                                  +---------+---------+
                                            |
                                            v
                                 +---------------------+
                                 |  Supervisor Agent   |
                                 +----------+----------+
                                            |
          +--------------------+------------+------------+--------------------+
          |                    |                         |                    |
          v                    v                         v                    v
+------------------+  +-----------------+      +-------------------+  +---------------+
| Doc Understanding|  |   Research      |      |     RAG Agent     |  | Content Gen   |
| (Structure/Style)|  |   (DuckDuckGo)  |      |   (ChromaDB Docs) |  | (Drafting)    |
+---------+--------+  +--------+--------+      +---------+---------+  +-------+-------+
          |                    |                         |                    |
          +--------------------+------------+------------+--------------------+
                                            |
                                            v
                              +---------------------------+
                              | Decision: Generate / Edit |
                              +-------------+-------------+
                                            |
                     +----------------------+----------------------+
                     |                                             |
                     v                                             v
        +-------------------------+                   +-------------------------+
        | Document Editing Agent  |                   | Document Gen Agent      |
        | - Targeted Run/Shape/   |                   | - Professional DOCX/    |
        |   Cell Replacement      |                   |   PPTX/XLSX builder     |
        | - Format Preservation   |                   +------------+------------+
        +------------+------------+                                |
                     |                                             |
                     +----------------------+----------------------+
                                            |
                                            v
                               +-------------------------+
                               |    Validation Agent     |
                               | (Format & Content check)|
                               +------------+------------+
                                            |
                                            v
                               +-------------------------+
                               |     Response Agent      |
                               | (Citations + Downloads) |
                               +-------------------------+
```

## 5. Document Structure & Formatting Preservation Strategy

1. **DOCX (Word)**:
   - Deep inspection of styles: Font family, size, RGB color, paragraph alignment, margins, header/footer references.
   - Run-level XML modification: To edit a paragraph without wiping bold/italic/font formatting, replace text inside existing `<w:r><w:t>` elements or clone formatting runs rather than recreating paragraphs.
   - Table Preservation: Edit cell paragraphs directly, retaining cell shading, borders, widths, and column grids.
   - Difference Tracker: Compare original XML structure vs modified XML structure to report exact additions, modifications, and deletions.

2. **PPTX (PowerPoint)**:
   - Slide Master & Layout Retention: Slide shapes inherit themes from slide masters. Targeted text replacement updates `<a:p><a:r><a:t>` inside shape text frames without resetting shape bounds, rotation, shadows, or colors.
   - New Slides: Cloned directly from existing slide layouts to inherit identical branding, fonts, and slide dimensions.

3. **XLSX (Excel)**:
   - Cell Value vs Style Decoupling: Updating a cell updates `.value` while retaining `.font`, `.border`, `.fill`, `.number_format`, and `.alignment`.
   - Formulas: Preserved explicitly (e.g., `=SUM(...)`), evaluated or updated dynamically if row ranges change.

## 6. Security & Data Isolation
- JWT token authentication with bcrypt password hashing.
- User-level workspace scoping: Every document, conversation, chunk, and generated file is partitioned by `user_id`.
- File upload sanitization: UUID filenames, extension whitelisting, size limits, path traversal prevention.
