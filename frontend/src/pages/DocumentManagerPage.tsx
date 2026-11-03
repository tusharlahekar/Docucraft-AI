import React, { useEffect, useState } from 'react';
import {
  FileText,
  Download,
  Trash2,
  FileCheck2,
  Layers,
  ArrowRight,
  GitCompare,
  Upload,
  RefreshCw,
  X
} from 'lucide-react';
import { api } from '../services/api';
import { UploadedDocument, GeneratedDocument } from '../types';

export const DocumentManagerPage: React.FC = () => {
  const [tab, setTab] = useState<'uploaded' | 'generated'>('uploaded');
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDocument[]>([]);
  const [generatedDocs, setGeneratedDocs] = useState<GeneratedDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedMeta, setSelectedMeta] = useState<any | null>(null);
  const [selectedDiff, setSelectedDiff] = useState<any | null>(null);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [uDocs, gDocs] = await Promise.all([
        api.listDocuments(),
        api.listGeneratedDocuments(),
      ]);
      setUploadedDocs(Array.isArray(uDocs) ? uDocs : []);
      setGeneratedDocs(Array.isArray(gDocs) ? gDocs : []);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setUploadedDocs([]);
      setGeneratedDocs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUploaded = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    try {
      await api.deleteDocument(id);
      setUploadedDocs((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  const handleInspectDiff = async (docId: string) => {
    try {
      const diffData = await api.getDiff(docId);
      setSelectedDiff(diffData);
    } catch (err) {
      console.error('Failed to get diff:', err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Document Repository & History</h1>
          <p className="text-sm text-slate-500 mt-1">
            Browse uploaded source documents and inspect generated or format-preserved artifacts.
          </p>
        </div>
        <button
          onClick={loadAll}
          className="flex items-center space-x-2 px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-600 hover:bg-slate-50 shadow-sm"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200 flex space-x-6">
        <button
          onClick={() => setTab('uploaded')}
          className={`pb-3 text-sm font-semibold flex items-center space-x-2 border-b-2 transition-colors ${
            tab === 'uploaded'
              ? 'border-brand-700 text-brand-700'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileText className="h-4 w-4" />
          <span>Uploaded Documents ({(uploadedDocs || []).length})</span>
        </button>
        <button
          onClick={() => setTab('generated')}
          className={`pb-3 text-sm font-semibold flex items-center space-x-2 border-b-2 transition-colors ${
            tab === 'generated'
              ? 'border-brand-700 text-brand-700'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileCheck2 className="h-4 w-4" />
          <span>Generated & Edited Documents ({(generatedDocs || []).length})</span>
        </button>
      </div>

      {/* Document Tables */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {tab === 'uploaded' ? (
          (uploadedDocs || []).length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">
              No documents uploaded yet. Upload DOCX, PPTX, XLSX, or PDF in the chat workspace.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600">
                <thead className="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-3">Document Name</th>
                    <th className="px-6 py-3">Format</th>
                    <th className="px-6 py-3">File Size</th>
                    <th className="px-6 py-3">Status</th>
                    <th className="px-6 py-3">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {(uploadedDocs || []).map((doc) => (
                    <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4 font-medium text-slate-900 flex items-center space-x-2.5">
                        <FileText className="h-4 w-4 text-brand-600 shrink-0" />
                        <span className="truncate max-w-xs">{doc.filename}</span>
                      </td>
                      <td className="px-6 py-4 uppercase font-bold text-xs">{doc.file_type}</td>
                      <td className="px-6 py-4">{Math.round(doc.file_size / 1024)} KB</td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                          {doc.parsed_status}
                        </span>
                      </td>
                      <td className="px-6 py-4 flex items-center space-x-3">
                        <button
                          onClick={() => setSelectedMeta(doc.metadata_summary)}
                          className="text-xs text-brand-700 hover:underline flex items-center space-x-1"
                        >
                          <Layers className="h-3.5 w-3.5" />
                          <span>Layout</span>
                        </button>
                        <a
                          href={api.getDocumentDownloadUrl(doc.id)}
                          target="_blank"
                          rel="noreferrer"
                          className="text-xs text-slate-600 hover:text-slate-900"
                        >
                          <Download className="h-4 w-4" />
                        </a>
                        <button
                          onClick={() => handleDeleteUploaded(doc.id)}
                          className="text-slate-400 hover:text-red-600"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : (generatedDocs || []).length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-sm">
            No generated or edited documents yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3">File Name</th>
                  <th className="px-6 py-3">Format</th>
                  <th className="px-6 py-3">Generation Type</th>
                  <th className="px-6 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {(generatedDocs || []).map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4 font-medium text-slate-900 flex items-center space-x-2.5">
                      <FileCheck2 className="h-4 w-4 text-emerald-600 shrink-0" />
                      <span className="truncate max-w-xs">{doc.filename}</span>
                    </td>
                    <td className="px-6 py-4 uppercase font-bold text-xs">{doc.file_type}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          doc.generation_type === 'edited_from_source'
                            ? 'bg-purple-100 text-purple-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {doc.generation_type === 'edited_from_source'
                          ? 'Format-Preserving Edit'
                          : 'New Creation'}
                      </span>
                    </td>
                    <td className="px-6 py-4 flex items-center space-x-3">
                      {doc.diff_summary && (
                        <button
                          onClick={() => handleInspectDiff(doc.id)}
                          className="text-xs text-brand-700 hover:underline flex items-center space-x-1"
                        >
                          <GitCompare className="h-3.5 w-3.5" />
                          <span>Diff</span>
                        </button>
                      )}
                      <a
                        href={api.getGeneratedDownloadUrl(doc.id)}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-emerald-700 font-semibold hover:underline flex items-center space-x-1"
                      >
                        <Download className="h-4 w-4" />
                        <span>Download</span>
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Layout Metadata Modal */}
      {selectedMeta && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-xl max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <h3 className="text-base font-bold text-slate-900">Extracted Document Layout & Styles</h3>
              <button onClick={() => setSelectedMeta(null)} className="text-slate-400 hover:text-slate-700">
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto pt-4 space-y-4 text-xs font-mono bg-slate-50 p-4 rounded-xl mt-3">
              <pre>{JSON.stringify(selectedMeta, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}

      {/* Diff Inspector Modal */}
      {selectedDiff && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-xl max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <h3 className="text-base font-bold text-slate-900">Document Comparison & Diff Audit</h3>
              <button onClick={() => setSelectedDiff(null)} className="text-slate-400 hover:text-slate-700">
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto pt-4 space-y-4 text-xs font-mono bg-slate-50 p-4 rounded-xl mt-3">
              <pre>{JSON.stringify(selectedDiff, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
