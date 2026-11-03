import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Paperclip,
  Bot,
  User,
  Download,
  ExternalLink,
  ChevronRight,
  ChevronDown,
  Sparkles,
  FileText,
  FileCheck2,
  Trash2,
  Plus,
  RefreshCw,
  Clock,
  Layers,
  CheckCircle2,
  AlertCircle,
  X
} from 'lucide-react';
import { api } from '../services/api';
import { Conversation, Message, UploadedDocument, AgentLog } from '../types';

export const ChatWorkspacePage: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputContent, setInputContent] = useState('');
  const [sending, setSending] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<UploadedDocument[]>([]);
  const [uploading, setUploading] = useState(false);
  const [showRightPanel, setShowRightPanel] = useState(true);
  const [activeDocForInspector, setActiveDocForInspector] = useState<UploadedDocument | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const convs = await api.listConversations();
      const safeConvs = Array.isArray(convs) ? convs : [];
      setConversations(safeConvs);
      if (safeConvs.length > 0 && !activeConvId) {
        selectConversation(safeConvs[0].id);
      } else if (safeConvs.length === 0) {
        handleNewChat();
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
      setConversations([]);
    }
  };

  const selectConversation = async (id: string) => {
    setActiveConvId(id);
    setAttachedFiles([]);
    setActiveDocForInspector(null);
    try {
      const conv = await api.getConversation(id);
      setMessages(Array.isArray(conv?.messages) ? conv.messages : []);
    } catch (err) {
      console.error('Failed to fetch conversation details:', err);
      setMessages([]);
    }
  };

  const handleNewChat = async () => {
    try {
      const newConv = await api.createConversation('New Conversation');
      if (newConv && newConv.id) {
        setConversations((prev) => [newConv, ...(Array.isArray(prev) ? prev : [])]);
        setActiveConvId(newConv.id);
        setMessages([]);
        setAttachedFiles([]);
      }
    } catch (err) {
      console.error('Failed to create new conversation:', err);
    }
  };

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.deleteConversation(id);
      const remaining = (conversations || []).filter((c) => c.id !== id);
      setConversations(remaining);
      if (activeConvId === id) {
        if (remaining.length > 0) {
          selectConversation(remaining[0].id);
        } else {
          handleNewChat();
        }
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    try {
      const file = files[0];
      const uploadedDoc = await api.uploadDocument(file, activeConvId || undefined);
      setAttachedFiles([...attachedFiles, uploadedDoc]);
      setActiveDocForInspector(uploadedDoc);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'File upload failed. Ensure DOCX, PPTX, XLSX, or PDF.');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleSendMessage = async (customPrompt?: string) => {
    const content = customPrompt || inputContent;
    if (!content.trim() || !activeConvId || sending) return;

    setInputContent('');
    setSending(true);

    // Optimistically add user message
    const tempUserMsg: Message = {
      id: `temp_${Date.now()}`,
      conversation_id: activeConvId,
      sender: 'user',
      content,
      attached_doc_ids: attachedFiles.map((f) => f.id),
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const docIds = attachedFiles.map((f) => f.id);
      const assistantMsg = await api.sendMessage(activeConvId, content, docIds);
      setMessages((prev) => [...prev.filter((m) => m.id !== tempUserMsg.id), tempUserMsg, assistantMsg]);
      // Refresh conversations in sidebar to update title if changed
      loadConversations();
    } catch (err: any) {
      console.error('Send message failed:', err);
      alert('Error communicating with AI agents. Ensure backend is running.');
    } finally {
      setSending(false);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-slate-100 overflow-hidden">
      {/* 1. Left Sidebar: Conversation History */}
      <div className="w-72 bg-white border-r border-slate-200 flex flex-col shrink-0">
        <div className="p-4 border-b border-slate-200">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center space-x-2 py-2.5 px-4 bg-brand-700 text-white rounded-lg text-sm font-semibold hover:bg-brand-800 transition-colors shadow-sm"
          >
            <Plus className="h-4 w-4" />
            <span>New Conversation</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          {(conversations || []).map((c) => (
            <div
              key={c.id}
              onClick={() => selectConversation(c.id)}
              className={`group flex items-center justify-between p-2.5 rounded-lg text-sm cursor-pointer transition-colors ${
                activeConvId === c.id
                  ? 'bg-brand-50 text-brand-900 font-medium border border-brand-200'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              <div className="flex items-center space-x-2.5 truncate">
                <FileText className={`h-4 w-4 shrink-0 ${activeConvId === c.id ? 'text-brand-600' : 'text-slate-400'}`} />
                <span className="truncate">{c.title || 'Untitled Session'}</span>
              </div>
              <button
                onClick={(e) => handleDeleteConversation(c.id, e)}
                className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-red-600 rounded transition-opacity"
                title="Delete Conversation"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 2. Main Chat Workspace */}
      <div className="flex-1 flex flex-col bg-slate-50 relative overflow-hidden">
        {/* Top Chat Bar */}
        <div className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between">
          <div className="flex items-center space-x-3 truncate">
            <Bot className="h-5 w-5 text-brand-700" />
            <h2 className="text-sm font-bold text-slate-800 truncate">
              {(conversations || []).find((c) => c.id === activeConvId)?.title || 'AI Document Assistant'}
            </h2>
            {(attachedFiles || []).length > 0 && (
              <span className="text-xs bg-brand-50 text-brand-700 px-2 py-0.5 rounded-full font-medium border border-brand-200">
                {attachedFiles.length} file(s) attached
              </span>
            )}
          </div>
          <button
            onClick={() => setShowRightPanel(!showRightPanel)}
            className="text-xs text-slate-500 hover:text-slate-900 font-medium flex items-center space-x-1 px-2.5 py-1.5 rounded-md hover:bg-slate-100 transition-colors"
          >
            <Layers className="h-4 w-4" />
            <span>{showRightPanel ? 'Hide Inspector' : 'Show Inspector'}</span>
          </button>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {(messages || []).length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto space-y-4">
              <div className="h-16 w-16 rounded-2xl bg-brand-50 border border-brand-100 flex items-center justify-center text-brand-700 shadow-sm">
                <Sparkles className="h-8 w-8" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900">What would you like to achieve?</h3>
                <p className="text-xs text-slate-500 mt-1">
                  Upload an existing DOCX, PPTX, XLSX, or PDF to edit while preserving formatting, or ask me to generate a new document from scratch.
                </p>
              </div>

              {/* Quick Prompt Pills */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full pt-2">
                <button
                  onClick={() => handleSendMessage('Create a professional Word report for quarterly strategy.')}
                  className="p-3 bg-white border border-slate-200 rounded-xl text-left hover:border-brand-300 hover:bg-brand-50/50 transition-all text-xs font-medium text-slate-700 shadow-sm"
                >
                  📄 Generate Word (.docx) Report
                </button>
                <button
                  onClick={() => handleSendMessage('Generate an executive PowerPoint presentation with 3 slides.')}
                  className="p-3 bg-white border border-slate-200 rounded-xl text-left hover:border-brand-300 hover:bg-brand-50/50 transition-all text-xs font-medium text-slate-700 shadow-sm"
                >
                  📊 Create PowerPoint (.pptx) Deck
                </button>
                <button
                  onClick={() => handleSendMessage('Build an Excel financial model with quarterly revenues and formulas.')}
                  className="p-3 bg-white border border-slate-200 rounded-xl text-left hover:border-brand-300 hover:bg-brand-50/50 transition-all text-xs font-medium text-slate-700 shadow-sm"
                >
                  📈 Build Excel (.xlsx) Model
                </button>
                <button
                  onClick={() => handleSendMessage('Update the company introduction and contact details, and preserve the exact original formatting.')}
                  className="p-3 bg-white border border-slate-200 rounded-xl text-left hover:border-brand-300 hover:bg-brand-50/50 transition-all text-xs font-medium text-slate-700 shadow-sm"
                >
                  ✨ Format-Preserving Document Edit
                </button>
              </div>
            </div>
          ) : (
            (messages || []).map((m) => <MessageCard key={m.id} message={m} />)
          )}

          {sending && (
            <div className="flex items-start space-x-3">
              <div className="h-8 w-8 rounded-lg bg-brand-700 text-white flex items-center justify-center shrink-0">
                <Bot className="h-4 w-4" />
              </div>
              <div className="p-4 bg-white border border-slate-200 rounded-2xl rounded-tl-none shadow-sm space-y-2">
                <div className="flex items-center space-x-2 text-xs font-semibold text-brand-700">
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                  <span>LangGraph Multi-Agent Pipeline Coordinating...</span>
                </div>
                <p className="text-xs text-slate-400">
                  Supervisor → Document Analysis → RAG Semantic Retrieval → Generation & Validation
                </p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Attached Files Strip */}
        {(attachedFiles || []).length > 0 && (
          <div className="bg-white border-t border-slate-200 px-6 py-2 flex items-center justify-between overflow-x-auto">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-semibold text-slate-500 uppercase">Attached:</span>
              {(attachedFiles || []).map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center space-x-1.5 px-2.5 py-1 bg-brand-50 border border-brand-200 rounded-md text-xs text-brand-800 font-medium group"
                >
                  <span
                    onClick={() => setActiveDocForInspector(doc)}
                    className="flex items-center space-x-1 cursor-pointer hover:underline"
                  >
                    <FileText className="h-3.5 w-3.5 text-brand-600" />
                    <span className="max-w-[150px] truncate">{doc.filename}</span>
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setAttachedFiles((prev) => prev.filter((d) => d.id !== doc.id));
                      if (activeDocForInspector?.id === doc.id) {
                        setActiveDocForInspector(null);
                      }
                    }}
                    className="p-0.5 hover:bg-brand-200 rounded text-brand-700 ml-1 transition-colors"
                    title="Remove attached file"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
            <button
              onClick={() => {
                setAttachedFiles([]);
                setActiveDocForInspector(null);
              }}
              className="text-xs text-slate-400 hover:text-red-600 font-medium whitespace-nowrap ml-3 transition-colors"
            >
              Clear Attachments
            </button>
          </div>
        )}

        {/* Bottom Input Area */}
        <div className="p-4 bg-white border-t border-slate-200">
          <div className="max-w-4xl mx-auto flex items-end space-x-3">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden"
              accept=".docx,.pptx,.xlsx,.pdf"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="p-3 text-slate-500 hover:text-brand-700 hover:bg-slate-100 rounded-xl transition-colors border border-slate-200 shadow-sm"
              title="Attach Document (DOCX, PPTX, XLSX, PDF)"
            >
              <Paperclip className="h-5 w-5" />
            </button>

            <div className="flex-1 relative">
              <textarea
                value={inputContent}
                onChange={(e) => setInputContent(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                placeholder={
                  attachedFiles.length > 0
                    ? 'Instruct changes (e.g. "Update introduction and maintain original formatting")...'
                    : 'Ask questions, request research, or generate DOCX/PPTX/XLSX...'
                }
                rows={1}
                className="w-full resize-none py-3 pl-4 pr-12 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 max-h-32"
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={!inputContent.trim() || sending}
                className="absolute right-2.5 bottom-2.5 p-1.5 bg-brand-700 text-white rounded-lg hover:bg-brand-800 transition-colors disabled:opacity-40"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Right Inspection Panel: Document Structure & Formatting Insights */}
      {showRightPanel && (
        <div className="w-80 bg-white border-l border-slate-200 flex flex-col shrink-0 overflow-y-auto">
          <div className="p-4 border-b border-slate-200">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <Layers className="h-4 w-4 text-brand-700" />
              <span>Document Structure Inspector</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Deep layout, font hierarchy, and formula analysis
            </p>
          </div>

          <div className="p-4 space-y-4">
            {activeDocForInspector ? (
              <div className="space-y-4">
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="flex items-center space-x-2">
                    <FileText className="h-4 w-4 text-brand-600" />
                    <span className="text-xs font-bold text-slate-900 truncate">
                      {activeDocForInspector.filename}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 mt-2 text-xs text-slate-500">
                    <span className="uppercase font-semibold">{activeDocForInspector.file_type}</span>
                    <span>•</span>
                    <span>{Math.round(activeDocForInspector.file_size / 1024)} KB</span>
                    <span>•</span>
                    <span className="text-emerald-600 font-medium">Parsed & Indexed</span>
                  </div>
                </div>

                {/* Structure Breakdown */}
                {activeDocForInspector.metadata_summary && (
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                      Extracted Layout Properties
                    </h4>

                    {/* Fonts */}
                    {Array.isArray(activeDocForInspector.metadata_summary.fonts) && activeDocForInspector.metadata_summary.fonts.length > 0 && (
                      <div className="text-xs">
                        <span className="font-semibold text-slate-600">Preserved Fonts:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {activeDocForInspector.metadata_summary.fonts.map((f: string) => (
                            <span key={f} className="px-2 py-0.5 bg-slate-100 rounded text-slate-700 font-mono">
                              {String(f)}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Colors */}
                    {Array.isArray(activeDocForInspector.metadata_summary.colors) && activeDocForInspector.metadata_summary.colors.length > 0 && (
                      <div className="text-xs">
                        <span className="font-semibold text-slate-600">Brand Color Palette:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {activeDocForInspector.metadata_summary.colors.map((c: string) => (
                            <span key={c} className="px-2 py-0.5 bg-slate-100 rounded text-slate-700 font-mono">
                              {String(c)}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Headings */}
                    {Array.isArray(activeDocForInspector.metadata_summary.headings) && activeDocForInspector.metadata_summary.headings.length > 0 && (
                      <div className="text-xs">
                        <span className="font-semibold text-slate-600">Document Headings:</span>
                        <ul className="list-disc pl-4 space-y-1 mt-1 text-slate-600">
                          {activeDocForInspector.metadata_summary.headings.slice(0, 5).map((h: any, i: number) => (
                            <li key={i} className="truncate">{h?.text || String(h)}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Tables or Sheets */}
                    {Array.isArray(activeDocForInspector.metadata_summary.tables) && activeDocForInspector.metadata_summary.tables.length > 0 && (
                      <div className="text-xs">
                        <span className="font-semibold text-slate-600">Tables Identified:</span>
                        <p className="text-slate-500 mt-0.5">
                          {activeDocForInspector.metadata_summary.tables.length} table(s) indexed with border & shading retention.
                        </p>
                      </div>
                    )}

                    {Array.isArray(activeDocForInspector.metadata_summary.sheets) && activeDocForInspector.metadata_summary.sheets.length > 0 && (
                      <div className="text-xs">
                        <span className="font-semibold text-slate-600">Spreadsheet Sheets:</span>
                        <ul className="list-disc pl-4 space-y-1 mt-1 text-slate-600">
                          {activeDocForInspector.metadata_summary.sheets.map((s: any, i: number) => (
                            <li key={i}>
                              {s?.name || 'Sheet'} ({s?.formulas_count ?? 0} formulas preserved)
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-xs text-slate-400">
                <FileText className="h-8 w-8 mx-auto mb-2 text-slate-300" />
                <span>Upload a document to inspect its full structural metadata and formatting rules.</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// ----------------- Message Card Component -----------------
const MessageCard: React.FC<{ message: Message }> = ({ message }) => {
  const [showLogs, setShowLogs] = useState(false);
  if (!message) return null;
  const isUser = message.sender === 'user';
  const citations = Array.isArray(message.citations) ? message.citations : [];
  const generatedDocIds = Array.isArray(message.generated_doc_ids) ? message.generated_doc_ids : [];
  const agentLogs = Array.isArray(message.agent_logs) ? message.agent_logs : [];

  return (
    <div className={`flex items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
      <div
        className={`h-8 w-8 rounded-lg flex items-center justify-center shrink-0 ${
          isUser ? 'bg-brand-700 text-white' : 'bg-slate-800 text-white'
        }`}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      <div
        className={`max-w-2xl rounded-2xl p-4 space-y-3 shadow-sm ${
          isUser
            ? 'bg-brand-700 text-white rounded-tr-none'
            : 'bg-white border border-slate-200 text-slate-900 rounded-tl-none'
        }`}
      >
        <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content || ''}</p>

        {/* Citations Badges */}
        {citations.length > 0 && (
          <div className="pt-2 border-t border-slate-100 space-y-1.5">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
              Verified Web Sources & Citations:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {citations.map((c: any, i: number) => {
                const url = typeof c === 'string' ? c : c?.url || '#';
                const title = typeof c === 'string' ? c : c?.title || url;
                return (
                  <a
                    key={i}
                    href={url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center space-x-1 px-2.5 py-1 bg-slate-100 hover:bg-slate-200 rounded text-xs text-brand-700 transition-colors max-w-xs truncate"
                  >
                    <span className="truncate">{title}</span>
                    <ExternalLink className="h-3 w-3 shrink-0" />
                  </a>
                );
              })}
            </div>
          </div>
        )}

        {/* Downloadable Generated Artifacts */}
        {generatedDocIds.length > 0 && (
          <div className="pt-2 border-t border-slate-100 space-y-2">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
              Downloadable File:
            </span>
            <div className="flex flex-wrap gap-2">
              {generatedDocIds.map((docId) => (
                <a
                  key={docId}
                  href={api.getGeneratedDownloadUrl(docId)}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center space-x-2 px-3 py-2 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-semibold hover:bg-emerald-100 transition-colors shadow-sm"
                >
                  <Download className="h-4 w-4 text-emerald-700" />
                  <span>Download Revised Document</span>
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Multi-Agent Execution Drawer */}
        {agentLogs.length > 0 && (
          <div className="pt-2 border-t border-slate-100">
            <button
              onClick={() => setShowLogs(!showLogs)}
              className="text-xs text-slate-500 hover:text-slate-800 font-medium flex items-center space-x-1"
            >
              {showLogs ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
              <span>Agent Execution Steps ({agentLogs.length})</span>
            </button>

            {showLogs && (
              <div className="mt-2 space-y-1.5 pl-2 border-l-2 border-brand-200 text-xs">
                {agentLogs.map((log: any, i: number) => (
                  <div key={i} className="py-1">
                    <span className="font-bold text-brand-700">{log?.agent || 'Agent'}: </span>
                    <span className="text-slate-700">{log?.step || ''} </span>
                    <span className="text-slate-400 font-mono">({log?.duration_ms || 0}ms)</span>
                    <p className="text-slate-500 mt-0.5">{log?.output || ''}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
