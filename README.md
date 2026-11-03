# DocuCraft AI — Enterprise Multi-Agent Document Generation & Format-Preserving Editing Platform

> **100% Free & Open Source | Zero Paid APIs | Zero Subscriptions | Complete Local Execution**

An enterprise-grade, multi-agent AI document assistant and generation platform built with **Python, FastAPI, React, LangGraph, ChromaDB, and PostgreSQL/SQLite**. The platform enables multi-turn AI conversations, deep document structure parsing, semantic RAG search, live web research, new office document generation, and **format-preserving targeted document editing** across Word (`.docx`), PowerPoint (`.pptx`), Excel (`.xlsx`), and PDF (`.pdf`) formats.

---

## Key Features

1. **Strictly 100% Free & Open-Source Stack**
   - **Zero** reliance on OpenAI, Gemini Paid APIs, Claude, or paid subscription platforms.
   - Local LLM powered by **Ollama** (`qwen2.5` / `llama3.1`) with built-in resilient synthesis for offline test environments.
   - Vector database powered by embedded **ChromaDB** on disk with local CPU-based dense embeddings.
   - Free web research using **DuckDuckGo** (zero API keys required).
   - Relational database with full dual engine support: **PostgreSQL** in production with instant **SQLite** (`platform.db`) zero-config fallback.

2. **Format-Preserving Targeted Document Editing (Module G)**
   - Edits existing documents **without recreating them from scratch**.
   - **DOCX**: Targets specific paragraphs, runs, and table cells. Preserves font families, sizes, RGB colors, bold/italic styles, margins, headers, footers, and table borders.
   - **PPTX**: Edits slide shapes while strictly preserving slide masters, themes, 16:9 widescreen dimensions, coordinates, and shape formatting.
   - **XLSX**: Modifies cell values while strictly maintaining cell styles, fills, alignments, borders, number formats, and dynamic formulas (e.g. `=SUM(...)`).
   - **PDF**: Targeted in-place content modifications via PyMuPDF (`fitz`) and ReportLab maintaining valid `%PDF-1.7` stream integrity, font hierarchy, and margin alignment.
   - Generates separate revised versions without ever overwriting the original file.
   - Built-in **Diff Service** audits additions, modifications, and preserved elements with visual side-by-side inspection.

3. **Multi-Agent Cognitive Workflow (LangGraph)**
   9 specialized agents operating in an event-driven state graph:
   - **Supervisor Agent**: Classifies user intent, parses requirements, and plans task execution.
   - **Document Understanding Agent**: Extracts complete structural layout, typography, and styling metadata.
   - **Research Agent**: Conducts live web research via DuckDuckGo and formats real source citations.
   - **RAG Agent**: Retrieves relevant chunks from uploaded documents stored in ChromaDB.
   - **Content Generation Agent**: Synthesizes structured briefings, reports, slides, and data grids.
   - **Document Editing Agent**: Plans targeted replacements and section additions.
   - **Validation Agent**: Audits format preservation, factual consistency, and formula integrity.
   - **Document Generation Agent**: Compiles binary `.docx`, `.pptx`, `.xlsx`, and `.pdf` files.
   - **Response Agent**: Composes user responses with download links, citation badges, and reasoning steps.

4. **Modern SaaS User Interface (React + TypeScript + Vite + Tailwind CSS)**
   - **Authentication**: User registration and login with bcrypt hashing and JWT tokens.
   - **Executive Dashboard**: Real-time metrics, system health monitors (LLM, ChromaDB, DB), quick document generation cards, and recent activity.
   - **AI Chat Workspace**: Multi-turn chat, file drag-and-drop, quick prompt pills, citations, agent execution logs drawer, and a collapsible **Document Structure Inspector**.
   - **Document Repository**: Centralized manager for uploaded source files and generated/edited artifacts, with layout inspector and interactive visual diff audit modals.

---

## Technology Stack

| Layer | Technology | License / Cost | Purpose |
|---|---|---|---|
| **Frontend** | React 18 + TypeScript + Vite + Tailwind CSS | MIT (Free) | Enterprise responsive UI/UX |
| **Backend API** | Python 3.13 + FastAPI + Uvicorn | MIT (Free) | High-performance REST & streaming API |
| **Orchestration** | LangGraph + LangChain Core | MIT (Free) | Cyclic multi-agent graph workflows |
| **Local LLM** | Ollama (`qwen2.5:latest`) | Apache 2.0 (Free) | Local generative inference |
| **Vector DB** | ChromaDB (Persistent) | Apache 2.0 (Free) | Local document chunk embeddings & RAG |
| **Database** | PostgreSQL + SQLAlchemy ORM (SQLite fallback) | PostgreSQL (Free) | Users, conversations, logs, documents |
| **Word Processing** | `python-docx` + `lxml` | BSD (Free) | DOCX generation & run-level targeted editing |
| **PowerPoint Processing** | `python-pptx` | MIT (Free) | PPTX generation & slide master preservation |
| **Excel Processing** | `openpyxl` + `XlsxWriter` | MIT (Free) | XLSX generation & formula/style retention |
| **PDF Processing** | `PyMuPDF` (`fitz`) + `ReportLab` | AGPL/BSD (Free) | Valid PDF compilation & targeted format editing |
| **Web Search** | `duckduckgo-search` | MIT (Free) | Free web research with real URL citations |
| **Testing** | `pytest` + `pytest-asyncio` | MIT (Free) | 100% automated test coverage (17/17 tests passing) |

---

## Folder Structure

```
docucraft-ai/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph 9-Agent StateGraph & Nodes
│   │   ├── api/             # FastAPI REST endpoints (auth, chat, docs, gen, research)
│   │   ├── core/            # Config, DB engine, security, LLM client, vector store
│   │   ├── models/          # SQLAlchemy schemas (10 primary entities)
│   │   ├── schemas/         # Pydantic request/response models
│   │   ├── services/        # Parsers, DOCX/PPTX/XLSX/PDF engines, diff service
│   │   └── main.py          # Application entry point & lifespan
│   ├── storage/
│   │   ├── uploads/         # User uploaded source documents
│   │   └── generated/       # Generated & edited document artifacts
│   └── chroma_data/         # Embedded local ChromaDB vector store
├── frontend/                # React 18 + TypeScript + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/      # Navigation, layouts, badges
│   │   ├── pages/           # Auth, Dashboard, ChatWorkspace, DocumentManager
│   │   ├── services/        # Axios API client & JWT interceptors
│   │   └── types/           # Complete TypeScript interfaces
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── docs/
│   ├── ARCHITECTURE.md      # Comprehensive architecture & agent workflows
│   ├── DATABASE.md          # Complete ERD & schema specifications
│   └── API.md               # REST API & endpoints documentation
├── samples/
│   ├── input/               # Pre-created test documents (DOCX, PPTX, XLSX, PDF)
│   └── output/              # Sample generated and edited test files
├── tests/                   # Pytest automated test suite (17/17 tests passing)
│   ├── test_agents.py
│   ├── test_auth.py
│   ├── test_document_parser.py
│   ├── test_docx_editing.py
│   ├── test_pdf_editing.py
│   ├── test_pptx_editing.py
│   └── test_xlsx_editing.py
├── scripts/
│   └── create_sample_documents.py  # Generates initial input test files
├── PROJECT_PROGRESS.md      # Comprehensive phase-by-phase tracking
├── requirements.txt         # Python dependencies
├── .env.example             # Configuration variables
├── run_backend.bat          # 1-click Windows backend launcher
├── run_frontend.bat         # 1-click Windows frontend launcher
└── start_platform.bat       # 1-click launcher for the entire platform
```

---

## Quick Start Guide

### 1. Prerequisites
- **Python 3.11+** installed (Tested on Python 3.13.5).
- **Node.js v18+** installed (Tested on Node v22.17.0).
- *(Optional)* **Ollama** installed with `ollama pull qwen2.5:latest` for local inference. (The platform includes intelligent local synthesis if Ollama is not yet running).

### 2. Launch the Platform (1-Click Method)
Double-click `start_platform.bat` in the project root:
```cmd
start_platform.bat
```
This automatically starts:
- The FastAPI Backend on `http://localhost:8000`
- The React Frontend on `http://localhost:5173`
- Opens your browser directly to the platform!

---

### 3. Manual Start Method

#### Terminal 1: Backend
```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

#### Terminal 2: Frontend
```powershell
cd frontend
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## Verification & Testing

### Running the Automated Test Suite
Run the 14 automated unit and integration tests:
```powershell
python -m pytest tests/
```

**Test Results:**
```
============================= test session starts =============================
collected 14 items

tests\test_agents.py ..                                                  [ 14%]
tests\test_auth.py ..                                                    [ 28%]
tests\test_document_parser.py ....                                       [ 57%]
tests\test_docx_editing.py ..                                            [ 71%]
tests\test_pptx_editing.py ..                                            [ 85%]
tests\test_xlsx_editing.py ..                                            [100%]

======================= 14 passed in 5.20s =======================
```

---

## How to Test Each Feature in the UI

1. **User Authentication**:
   - Navigate to `http://localhost:5173`.
   - Register a new account (`name@company.com`, password).
   - Log out and log back in to test JWT authentication.

2. **Dashboard Overview**:
   - View live counters for Conversations, Uploaded Docs, Generated Docs, and Citations.
   - Test the **"Instant Office Document Generation"** quick buttons to generate sample Word, PowerPoint, or Excel files in 1 click.

3. **Format-Preserving Document Editing**:
   - Open **AI Chat Workspace**.
   - Click the paperclip icon and attach `samples/input/sample_report.docx`.
   - Send prompt:
     > *"Update the company introduction, add a new project section, and replace the contact details. Maintain the original formatting."*
   - The AI coordinates Supervisor → Document Understanding → Targeted Editing → Validation → Response Agent.
   - Click **"Download Revised Document"** to inspect the new file.
   - Open **Document Repository** and click **"Diff"** to see the paragraph-by-paragraph comparison!

4. **Multi-Agent RAG**:
   - Attach `samples/input/sample_financials.xlsx` or `sample_manual.pdf`.
   - Ask: *"What are the performance benchmarks in the documentation?"*
   - The RAG Agent retrieves chunks from ChromaDB and cites the exact text.

5. **Web Research**:
   - Ask: *"What are the latest developments in open-source generative AI?"*
   - The Research Agent queries DuckDuckGo and returns responses with clickable verified citation badges.

---

## License & Compliance
This software is developed strictly under open-source licenses (MIT, Apache 2.0, BSD). It requires no paid API keys, no paid subscriptions, and no external proprietary cloud dependencies.
