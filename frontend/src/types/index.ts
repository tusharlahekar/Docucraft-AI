export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Citation {
  title: string;
  url: string;
  snippet?: string;
  retrieval_date?: string;
}

export interface AgentLog {
  agent: string;
  step: string;
  input: string;
  output: string;
  duration_ms: number;
  timestamp: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  citations?: Citation[];
  attached_doc_ids?: string[];
  generated_doc_ids?: string[];
  agent_logs?: AgentLog[];
  created_at: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface UploadedDocument {
  id: string;
  filename: string;
  file_type: 'docx' | 'pptx' | 'xlsx' | 'pdf';
  file_size: number;
  parsed_status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  metadata_summary?: Record<string, any>;
}

export interface GeneratedDocument {
  id: string;
  filename: string;
  file_type: 'docx' | 'pptx' | 'xlsx';
  file_size: number;
  generation_type: 'created_from_scratch' | 'edited_from_source';
  diff_summary?: Record<string, any>;
  created_at: string;
}

export interface DashboardStats {
  metrics: {
    total_conversations: number;
    total_uploaded_documents: number;
    total_generated_documents: number;
    total_research_queries: number;
  };
  recent_activity: {
    conversations: Array<{ id: string; title: string; updated_at: string }>;
    generated_documents: Array<{
      id: string;
      filename: string;
      file_type: string;
      generation_type: string;
      created_at: string;
    }>;
  };
  system_health: {
    llm: {
      status: string;
      available: boolean;
      models: string[];
      current_model: string;
    };
    vector_db: {
      engine: string;
      status: string;
      total_chunks_indexed: number;
    };
    database: {
      driver: string;
      status: string;
    };
  };
}
