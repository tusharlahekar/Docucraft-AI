import React, { useState } from 'react';
import { Bot, Lock, Mail, User, ShieldCheck, ArrowRight, Sparkles, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { User as UserType } from '../types';

interface AuthPageProps {
  onAuthSuccess: (user: UserType, token: string) => void;
}

export const AuthPage: React.FC<AuthPageProps> = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isLogin) {
        const res = await api.login(email, password);
        localStorage.setItem('token', res.access_token);
        onAuthSuccess(res.user, res.access_token);
      } else {
        const res = await api.register(email, password, fullName);
        localStorage.setItem('token', res.access_token);
        onAuthSuccess(res.user, res.access_token);
      }
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((d: any) => d.msg || JSON.stringify(d)).join(', '));
      } else if (typeof detail === 'string') {
        setError(detail);
      } else if (err.message) {
        setError(`Error: ${err.message}. Please verify the backend is running at http://localhost:8000.`);
      } else {
        setError('Authentication failed. Please check your credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-slate-100 to-brand-50 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full grid grid-cols-1 md:grid-cols-2 bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
        {/* Left hero banner */}
        <div className="bg-gradient-to-br from-brand-800 to-brand-950 p-8 text-white flex flex-col justify-between">
          <div>
            <div className="h-12 w-12 rounded-xl bg-white/10 backdrop-blur border border-white/20 flex items-center justify-center mb-6">
              <Bot className="h-7 w-7 text-white" />
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight mb-2">
              DocuAI Platform
            </h1>
            <p className="text-brand-200 text-sm mb-6">
              Enterprise AI Chatbot & Document Generation Platform with Guaranteed Format Preservation.
            </p>

            <div className="space-y-3">
              <div className="flex items-center space-x-3 text-sm">
                <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                <span>Multi-Turn Agentic Chatbot (LangGraph)</span>
              </div>
              <div className="flex items-center space-x-3 text-sm">
                <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                <span>Format-Preserving DOCX, PPTX & XLSX Editing</span>
              </div>
              <div className="flex items-center space-x-3 text-sm">
                <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                <span>Local ChromaDB Semantic Vector RAG</span>
              </div>
              <div className="flex items-center space-x-3 text-sm">
                <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                <span>100% Free & Open-Source (Zero Cloud Fees)</span>
              </div>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-white/10 text-xs text-brand-300">
            Powered by FastAPI, LangGraph, Ollama, ChromaDB & PostgreSQL.
          </div>
        </div>

        {/* Right form card */}
        <div className="p-8 flex flex-col justify-center">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-slate-900">
              {isLogin ? 'Sign In to Your Workspace' : 'Create an Account'}
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              {isLogin
                ? 'Enter your credentials to access your document sessions'
                : 'Start generating and editing documents locally'}
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex flex-col space-y-1">
              <span>{error}</span>
              {!isLogin && error.includes('already exists') && (
                <button
                  type="button"
                  onClick={() => {
                    setIsLogin(true);
                    setError(null);
                  }}
                  className="text-xs font-bold text-brand-700 hover:underline text-left mt-1"
                >
                  👉 Click here to switch to Sign In with this email
                </button>
              )}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Full Name
                </label>
                <div className="relative">
                  <User className="h-5 w-5 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Alex Johnson"
                    className="w-full pl-10 pr-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="h-5 w-5 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full pl-10 pr-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="h-5 w-5 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full pl-10 pr-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 bg-brand-700 hover:bg-brand-800 text-white font-medium rounded-lg shadow transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {loading ? (
                <span>Authenticating...</span>
              ) : (
                <>
                  <span>{isLogin ? 'Sign In' : 'Create Free Account'}</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-slate-600">
            {isLogin ? "Don't have an account yet?" : 'Already have an account?'}{' '}
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError(null);
              }}
              className="text-brand-700 font-semibold hover:underline"
            >
              {isLogin ? 'Sign Up' : 'Sign In'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
