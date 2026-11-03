import React, { useEffect, useState } from 'react';
import {
  MessageSquare,
  FileText,
  FileCheck2,
  Search,
  Sparkles,
  ArrowUpRight,
  Database,
  Cpu,
  HardDrive,
  Upload,
  Plus
} from 'lucide-react';
import { api } from '../services/api';
import { DashboardStats } from '../types';

interface DashboardPageProps {
  onStartChat: () => void;
  onViewDocuments: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onStartChat, onViewDocuments }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleQuickGenerate = async (type: 'docx' | 'pptx' | 'xlsx') => {
    setGenerating(type);
    try {
      const title = `Executive ${type.toUpperCase()} Overview`;
      const doc = await api.generateDocument(type, title, 'Quick Generation from Dashboard');
      window.open(api.getGeneratedDownloadUrl(doc.id), '_blank');
      fetchStats();
    } catch (err) {
      console.error('Quick generation failed:', err);
    } finally {
      setGenerating(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Executive Control Center</h1>
          <p className="text-sm text-slate-500 mt-1">
            Real-time monitoring of AI agents, document processing pipelines, and local semantic storage.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={onViewDocuments}
            className="flex items-center space-x-2 px-4 py-2 bg-white border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
          >
            <Upload className="h-4 w-4" />
            <span>Upload Document</span>
          </button>
          <button
            onClick={onStartChat}
            className="flex items-center space-x-2 px-4 py-2 bg-brand-700 text-white rounded-lg text-sm font-medium hover:bg-brand-800 transition-colors shadow-sm shadow-brand-700/20"
          >
            <Plus className="h-4 w-4" />
            <span>New Chat Session</span>
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Conversations</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">
              {stats?.metrics.total_conversations ?? 0}
            </h3>
            <p className="text-xs text-emerald-600 mt-1 flex items-center">
              Active sessions indexed
            </p>
          </div>
          <div className="h-12 w-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <MessageSquare className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Uploaded Documents</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">
              {stats?.metrics.total_uploaded_documents ?? 0}
            </h3>
            <p className="text-xs text-blue-600 mt-1 flex items-center">
              DOCX, PPTX, XLSX & PDF
            </p>
          </div>
          <div className="h-12 w-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <FileText className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Generated Artifacts</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">
              {stats?.metrics.total_generated_documents ?? 0}
            </h3>
            <p className="text-xs text-emerald-600 mt-1 flex items-center">
              Format preservation active
            </p>
          </div>
          <div className="h-12 w-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <FileCheck2 className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Web Citations</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">
              {stats?.metrics.total_research_queries ?? 0}
            </h3>
            <p className="text-xs text-purple-600 mt-1 flex items-center">
              100% Free search queries
            </p>
          </div>
          <div className="h-12 w-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
            <Search className="h-6 w-6" />
          </div>
        </div>
      </div>

      {/* Quick Document Generation Cards */}
      <div className="bg-gradient-to-r from-brand-900 to-slate-900 rounded-2xl p-6 text-white shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-lg font-bold">Instant Office Document Generation</h2>
            <p className="text-sm text-slate-300">
              Generate ready-to-use professional business documents formatted with corporate themes.
            </p>
          </div>
          <span className="text-xs bg-white/10 px-3 py-1 rounded-full text-brand-200 border border-white/20">
            Open-Source Native Engines
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/10 flex flex-col justify-between">
            <div>
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-400/30">
                Word (.docx)
              </span>
              <h4 className="text-base font-semibold mt-2">Executive Report</h4>
              <p className="text-xs text-slate-300 mt-1">
                Structured headings, executive typography, data tables, and headers/footers.
              </p>
            </div>
            <button
              onClick={() => handleQuickGenerate('docx')}
              disabled={generating !== null}
              className="mt-4 w-full py-2 bg-white text-slate-900 font-semibold rounded-lg text-xs hover:bg-slate-100 transition-colors flex items-center justify-center space-x-1"
            >
              <span>{generating === 'docx' ? 'Compiling...' : 'Generate & Download'}</span>
              <ArrowUpRight className="h-4 w-4" />
            </button>
          </div>

          <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/10 flex flex-col justify-between">
            <div>
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-orange-500/20 text-orange-300 border border-orange-400/30">
                PowerPoint (.pptx)
              </span>
              <h4 className="text-base font-semibold mt-2">Presentation Deck</h4>
              <p className="text-xs text-slate-300 mt-1">
                16:9 widescreen layout, slide masters, structured agendas, and visual hierarchies.
              </p>
            </div>
            <button
              onClick={() => handleQuickGenerate('pptx')}
              disabled={generating !== null}
              className="mt-4 w-full py-2 bg-white text-slate-900 font-semibold rounded-lg text-xs hover:bg-slate-100 transition-colors flex items-center justify-center space-x-1"
            >
              <span>{generating === 'pptx' ? 'Compiling...' : 'Generate & Download'}</span>
              <ArrowUpRight className="h-4 w-4" />
            </button>
          </div>

          <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/10 flex flex-col justify-between">
            <div>
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                Excel (.xlsx)
              </span>
              <h4 className="text-base font-semibold mt-2">Financial Workbook</h4>
              <p className="text-xs text-slate-300 mt-1">
                Dynamic `=SUM()` formulas, currency formatting, header fills, and multi-sheet grids.
              </p>
            </div>
            <button
              onClick={() => handleQuickGenerate('xlsx')}
              disabled={generating !== null}
              className="mt-4 w-full py-2 bg-white text-slate-900 font-semibold rounded-lg text-xs hover:bg-slate-100 transition-colors flex items-center justify-center space-x-1"
            >
              <span>{generating === 'xlsx' ? 'Compiling...' : 'Generate & Download'}</span>
              <ArrowUpRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Two Column Layout: System Status & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Health */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
            <Cpu className="h-5 w-5 text-brand-700" />
            <span>Infrastructure Health</span>
          </h3>

          <div className="space-y-3">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-700">Local LLM Engine</p>
                <p className="text-xs text-slate-500">
                  {stats?.system_health.llm.status === 'connected' ? 'Ollama Daemon Active' : 'Intelligent Local Synthesizer'}
                </p>
              </div>
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 ring-4 ring-emerald-100"></span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-700">Vector Storage</p>
                <p className="text-xs text-slate-500">
                  ChromaDB ({stats?.system_health.vector_db.total_chunks_indexed ?? 0} Chunks)
                </p>
              </div>
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 ring-4 ring-emerald-100"></span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-700">Main Database</p>
                <p className="text-xs text-slate-500">
                  {stats?.system_health.database.driver ?? 'SQLAlchemy ORM'}
                </p>
              </div>
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 ring-4 ring-emerald-100"></span>
            </div>
          </div>
        </div>

        {/* Recent Generated Files & Activity */}
        <div className="lg:col-span-2 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
              <HardDrive className="h-5 w-5 text-brand-700" />
              <span>Recent Document Artifacts</span>
            </h3>
            <button onClick={onViewDocuments} className="text-xs text-brand-700 font-semibold hover:underline">
              View All
            </button>
          </div>

          <div className="divide-y divide-slate-100">
            {stats?.recent_activity.generated_documents.length === 0 ? (
              <p className="text-sm text-slate-400 py-6 text-center">
                No documents generated yet. Use the quick buttons above or chat with the AI!
              </p>
            ) : (
              stats?.recent_activity.generated_documents.map((doc) => (
                <div key={doc.id} className="py-3 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span
                      className={`text-xs uppercase font-bold px-2 py-1 rounded ${
                        doc.file_type === 'docx'
                          ? 'bg-blue-100 text-blue-800'
                          : doc.file_type === 'pptx'
                          ? 'bg-orange-100 text-orange-800'
                          : 'bg-emerald-100 text-emerald-800'
                      }`}
                    >
                      {doc.file_type}
                    </span>
                    <div>
                      <p className="text-sm font-medium text-slate-800">{doc.filename}</p>
                      <p className="text-xs text-slate-400">
                        {doc.generation_type === 'edited_from_source'
                          ? 'Format-Preserving Revision'
                          : 'Created from scratch'}
                      </p>
                    </div>
                  </div>
                  <a
                    href={api.getGeneratedDownloadUrl(doc.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-brand-700 font-semibold hover:underline flex items-center space-x-1"
                  >
                    <span>Download</span>
                    <ArrowUpRight className="h-3 w-3" />
                  </a>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
