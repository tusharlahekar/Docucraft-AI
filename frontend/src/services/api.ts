import axios from 'axios';
import {
  AuthResponse,
  User,
  Conversation,
  Message,
  UploadedDocument,
  GeneratedDocument,
  DashboardStats
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // Auth
  register: async (email: string, password: string, full_name: string): Promise<AuthResponse> => {
    const res = await apiClient.post('/auth/register', { email, password, full_name });
    return res.data;
  },

  login: async (email: string, password: string): Promise<AuthResponse> => {
    const res = await apiClient.post('/auth/login', { email, password });
    return res.data;
  },

  getProfile: async (): Promise<User> => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },

  // Conversations
  listConversations: async (): Promise<Conversation[]> => {
    const res = await apiClient.get('/conversations');
    return Array.isArray(res.data) ? res.data : [];
  },

  createConversation: async (title?: string): Promise<Conversation> => {
    const res = await apiClient.post('/conversations', { title });
    return res.data;
  },

  getConversation: async (id: string): Promise<Conversation> => {
    const res = await apiClient.get(`/conversations/${id}`);
    return res.data;
  },

  deleteConversation: async (id: string): Promise<void> => {
    await apiClient.delete(`/conversations/${id}`);
  },

  // Chat
  sendMessage: async (
    conversationId: string,
    content: string,
    attachedDocIds: string[] = []
  ): Promise<Message> => {
    const res = await apiClient.post(`/chat/${conversationId}/send`, {
      content,
      attached_doc_ids: attachedDocIds,
    });
    return res.data;
  },

  // Documents
  uploadDocument: async (file: File, conversationId?: string): Promise<UploadedDocument> => {
    const formData = new FormData();
    formData.append('file', file);
    if (conversationId) {
      formData.append('conversation_id', conversationId);
    }
    const res = await apiClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  listDocuments: async (): Promise<UploadedDocument[]> => {
    const res = await apiClient.get('/documents');
    return Array.isArray(res.data) ? res.data : [];
  },

  getDocument: async (id: string): Promise<UploadedDocument> => {
    const res = await apiClient.get(`/documents/${id}`);
    return res.data;
  },

  deleteDocument: async (id: string): Promise<void> => {
    await apiClient.delete(`/documents/${id}`);
  },

  getDocumentDownloadUrl: (id: string): string => {
    const token = localStorage.getItem('token');
    return `${API_BASE_URL}/documents/${id}/download${token ? `?token=${encodeURIComponent(token)}` : ''}`;
  },

  // Document Generation & Editing
  generateDocument: async (
    fileType: 'docx' | 'pptx' | 'xlsx',
    title: string,
    subtitle?: string,
    conversationId?: string
  ): Promise<GeneratedDocument> => {
    const res = await apiClient.post('/generation/generate', {
      file_type: fileType,
      title,
      subtitle,
      conversation_id: conversationId,
    });
    return res.data;
  },

  editDocument: async (
    documentId: string,
    instructions: string,
    replacements?: Record<string, string>,
    conversationId?: string
  ): Promise<GeneratedDocument> => {
    const res = await apiClient.post('/generation/edit', {
      document_id: documentId,
      instructions,
      replacements,
      conversation_id: conversationId,
    });
    return res.data;
  },

  listGeneratedDocuments: async (): Promise<GeneratedDocument[]> => {
    const res = await apiClient.get('/generation');
    return Array.isArray(res.data) ? res.data : [];
  },

  getGeneratedDownloadUrl: (id: string): string => {
    const token = localStorage.getItem('token');
    return `${API_BASE_URL}/generation/${id}/download${token ? `?token=${encodeURIComponent(token)}` : ''}`;
  },

  getDiff: async (id: string): Promise<any> => {
    const res = await apiClient.get(`/generation/${id}/diff`);
    return res.data;
  },

  // Dashboard
  getDashboardStats: async (): Promise<DashboardStats> => {
    const res = await apiClient.get('/dashboard/stats');
    return res.data;
  },

  // Web Research
  performSearch: async (query: string, maxResults = 5) => {
    const res = await apiClient.post('/research/search', { query, max_results: maxResults });
    return res.data;
  },
};
