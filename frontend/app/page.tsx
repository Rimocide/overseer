'use client';

import { useState, useRef, useEffect } from 'react';
import { Toaster, toast } from 'sonner';
import { Send, Sparkles, User, Settings2, ArrowRight, Loader2, Database, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/cjs/styles/prism';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

function CodeBlock({ language, code }: { language: string; code: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="my-4 rounded-xl overflow-hidden border border-zinc-800/60 bg-[#121214] shadow-sm max-w-full">
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#18181b] border-b border-zinc-800/60">
        <span className="text-xs text-zinc-400 font-mono lowercase">{language || 'text'}</span>
        <button onClick={handleCopy} className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-100 transition-colors">
          {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
      {}
      <div className="overflow-x-auto max-w-full">
        <SyntaxHighlighter
          language={language}
          style={oneDark}
          PreTag="div"
          customStyle={{
            margin: 0,
            padding: '1rem',
            background: 'transparent',
            fontSize: '13px',
            lineHeight: 1.6,
            minWidth: 'fit-content'
          }}
          codeTagProps={{
            style: { backgroundColor: 'transparent', fontFamily: 'inherit' }
          }}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}

const markdownComponents = {
  pre({ children }: any) {
    const child = Array.isArray(children) ? children[0] : children;
    const codeProps = child?.props || {};
    const match = /language-(\w+)/.exec(codeProps.className || '');
    const language = match ? match[1] : 'text';
    const code = String(codeProps.children ?? '').replace(/\n$/, '');
    return <CodeBlock language={language} code={code} />;
  },
  code({ children, ...props }: any) {

    return (
      <code className="bg-zinc-800/40 border border-zinc-800/60 text-zinc-200 rounded px-1.5 py-0.5 text-[13px] font-mono" {...props}>
        {children}
      </code>
    );
  },
  p({ children }: any) {
    return <p className="mb-3 last:mb-0">{children}</p>;
  },
  ul({ children }: any) {
    return <ul className="mb-3 pl-5 space-y-1 list-disc marker:text-zinc-600">{children}</ul>;
  },
  ol({ children }: any) {
    return <ol className="mb-3 pl-5 space-y-1 list-decimal marker:text-zinc-600">{children}</ol>;
  },
  li({ children }: any) {
    return <li className="pl-1">{children}</li>;
  },
  a({ href, children }: any) {
    return (
      <a href={href} target="_blank" rel="noreferrer" className="text-[#fe7f2d] underline underline-offset-2 hover:text-[#ff9752]">
        {children}
      </a>
    );
  },
  blockquote({ children }: any) {
    return <blockquote className="border-l-2 border-zinc-700 pl-3 italic text-zinc-400 my-3">{children}</blockquote>;
  },
  h1({ children }: any) {
    return <h1 className="text-lg font-semibold mt-4 mb-2 text-zinc-50">{children}</h1>;
  },
  h2({ children }: any) {
    return <h2 className="text-base font-semibold mt-4 mb-2 text-zinc-50">{children}</h2>;
  },
  h3({ children }: any) {
    return <h3 className="text-sm font-semibold mt-3 mb-2 text-zinc-50">{children}</h3>;
  },
  hr() {
    return <hr className="border-zinc-800 my-4" />;
  },
  table({ children }: any) {
    return (
      <div className="overflow-x-auto my-3 max-w-full">
        <table className="min-w-full border border-zinc-800 text-sm">{children}</table>
      </div>
    );
  },
  th({ children }: any) {
    return <th className="border border-zinc-800 bg-zinc-900 px-3 py-2 text-left font-medium text-zinc-300">{children}</th>;
  },
  td({ children }: any) {
    return <td className="border border-zinc-800 px-3 py-2 text-zinc-300">{children}</td>;
  },
};

export default function WorkspaceChat() {
  const [showConfig, setShowConfig] = useState(true);
  const [loading, setLoading] = useState(false);
  const [envReady, setEnvReady] = useState(false);
  const [config, setConfig] = useState({
    owner: '',
    repo: '',
    geminiKey: '',
    pineconeKey: '',
    githubToken: ''
  });

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch('/api/index-repo')
      .then(res => res.json())
      .then(data => {
        if (data.hasEnv) setEnvReady(true);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const canSkip = envReady || Boolean(config.geminiKey && config.pineconeKey && config.githubToken);

  const runIngestionPipeline = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch('/api/index-repo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });

      if (!res.ok) throw new Error('Ingestion Failed');

      toast.success("Workspace synced to Pinecone successfully!");
      setShowConfig(false);
    } catch {
      toast.error("Pipeline initialization failed. Check your API keys.");
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    const text = chatInput.trim();
    if (!text || isLoading) return;

    const userMessage: ChatMessage = { id: Date.now().toString(), role: 'user', content: text };
    const historyForRequest = [...messages, userMessage];

    setMessages(historyForRequest);
    setChatInput('');
    setIsLoading(true);

    const assistantId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: '' }]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: historyForRequest }),
      });

      if (!response.ok || !response.body) {
        throw new Error('Stream request failed');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setMessages(prev =>
          prev.map(m => (m.id === assistantId ? { ...m, content: m.content + chunk } : m))
        );
      }
    } catch {
      toast.error("Lost connection to the Overseer.");
      setMessages(prev => prev.filter(m => !(m.id === assistantId && m.content === '')));
    } finally {
      setIsLoading(false);
    }
  };

  if (showConfig) {
    return (
      <div className="min-h-screen w-full flex flex-col items-center justify-center bg-[#09090b] text-zinc-50 p-4 font-sans">
        <Toaster position="top-center" richColors theme="dark" />

        <div className="max-w-md w-full space-y-8">
          <div className="text-center space-y-2">
            <div className="mx-auto bg-[#233d4d] w-12 h-12 flex items-center justify-center rounded-xl mb-6 shadow-lg shadow-[#233d4d]/20">
              <Database className="text-white w-6 h-6" />
            </div>
            <h1 className="text-2xl font-medium tracking-tight">The Overseer</h1>
            <p className="text-zinc-400 text-sm">Configure your ingestion targets or access the active vector space directly.</p>
          </div>

          <form onSubmit={runIngestionPipeline} className="space-y-4 bg-zinc-900/50 p-6 rounded-2xl border border-zinc-800/50 backdrop-blur-xl">
            <div className="space-y-3">
              <input type="password" value={config.geminiKey} onChange={e => setConfig({...config, geminiKey: e.target.value})} placeholder="Gemini API Key (Leave blank for .env)" className="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-[#fe7f2d] focus:ring-1 focus:ring-[#fe7f2d] transition-all placeholder:text-zinc-600" />
              <input type="password" value={config.pineconeKey} onChange={e => setConfig({...config, pineconeKey: e.target.value})} placeholder="Pinecone API Key (Leave blank for .env)" className="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-[#fe7f2d] focus:ring-1 focus:ring-[#fe7f2d] transition-all placeholder:text-zinc-600" />
              <input type="password" value={config.githubToken} onChange={e => setConfig({...config, githubToken: e.target.value})} placeholder="GitHub PAT Token (Leave blank for .env)" className="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-[#fe7f2d] focus:ring-1 focus:ring-[#fe7f2d] transition-all placeholder:text-zinc-600" />
              <div className="flex gap-3">
                <input value={config.owner} onChange={e => setConfig({...config, owner: e.target.value})} placeholder="Repo Owner" className="w-1/2 bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-[#fe7f2d] focus:ring-1 focus:ring-[#fe7f2d] transition-all placeholder:text-zinc-600" />
                <input value={config.repo} onChange={e => setConfig({...config, repo: e.target.value})} placeholder="Repository" className="w-1/2 bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-[#fe7f2d] focus:ring-1 focus:ring-[#fe7f2d] transition-all placeholder:text-zinc-600" />
              </div>
            </div>

            <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 bg-[#233d4d] hover:bg-[#fe7f2d] text-white py-3 rounded-xl font-medium text-sm transition-all duration-300 disabled:opacity-50">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Database className="w-4 h-4" />}
              {loading ? 'Ingesting Repository...' : 'Build Vector Context'}
            </button>

            <button type="button" onClick={() => setShowConfig(false)} disabled={!canSkip} className="w-full flex items-center justify-center gap-2 bg-transparent hover:bg-zinc-800 text-zinc-400 hover:text-white py-3 rounded-xl font-medium text-sm transition-all duration-300 disabled:opacity-30 disabled:hover:bg-transparent disabled:cursor-not-allowed">
              Skip directly to Chat <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen w-full bg-[#09090b] text-zinc-100 font-sans selection:bg-[#fe7f2d]/30">
      <Toaster position="top-center" richColors theme="dark" />

      <header className="flex-none flex items-center justify-between px-6 py-4 border-b border-zinc-800/60 bg-[#09090b]/80 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="bg-[#233d4d] p-1.5 rounded-lg">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <span className="font-medium text-sm tracking-wide">The Overseer</span>
          {(config.owner && config.repo) && (
            <span className="ml-2 text-xs px-2 py-1 bg-zinc-900 border border-zinc-800 rounded-md text-zinc-400">
              {config.owner}/{config.repo}
            </span>
          )}
        </div>
        <button onClick={() => setShowConfig(true)} className="p-2 text-zinc-400 hover:text-[#fe7f2d] hover:bg-[#fe7f2d]/10 rounded-lg transition-colors" title="Settings">
          <Settings2 className="w-5 h-5" />
        </button>
      </header>

      <main className="flex-1 overflow-y-auto pb-32 pt-8">
        <div className="max-w-3xl mx-auto px-4 space-y-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-4 opacity-50">
              <Sparkles className="w-8 h-8 text-zinc-500" />
              <p className="text-zinc-400 text-sm max-w-sm">
                You are connected to the runtime vector space. Ask about architecture, flows, or implementation details.
              </p>
            </div>
          ) : (
            messages.map((m) => (
              <div key={m.id} className="flex gap-4 group">
                <div className={`flex-none w-8 h-8 rounded-lg flex items-center justify-center shadow-sm ${m.role === 'user' ? 'bg-zinc-800 border border-zinc-700' : 'bg-[#233d4d]'}`}>
                  {m.role === 'user' ? <User className="w-5 h-5 text-zinc-300" /> : <Sparkles className="w-5 h-5 text-white" />}
                </div>
                <div className="flex-1 min-w-0 space-y-2 mt-1">
                  <span className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                    {m.role === 'user' ? 'You' : 'The Overseer'}
                  </span>
                  <div className="text-[15px] leading-relaxed text-zinc-200">
                    <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]} components={markdownComponents}>
                      {m.content}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            ))
          )}
          {isLoading && messages[messages.length - 1]?.content === '' && (
            <div className="flex gap-4 animate-pulse">
               <div className="flex-none w-8 h-8 rounded-lg bg-[#233d4d]/50 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white/50" />
                </div>
                <div className="flex-1 mt-1">
                  <div className="h-4 bg-zinc-800 rounded w-1/4"></div>
                </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <div className="fixed bottom-0 w-full bg-gradient-to-t from-[#09090b] via-[#09090b] to-transparent pb-6 pt-12">
        <div className="max-w-3xl mx-auto px-4">
          <form onSubmit={handleSendMessage} className="relative flex items-center shadow-2xl">
            <input
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              placeholder="Ask anything..."
              className="w-full bg-zinc-900 border border-zinc-800 rounded-2xl pl-5 pr-14 py-4 text-[15px] text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:border-zinc-700 focus:ring-1 focus:ring-zinc-700 transition-all shadow-sm"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !chatInput.trim()}
              className="absolute right-2 p-2 bg-[#233d4d] hover:bg-[#fe7f2d] disabled:bg-zinc-800 disabled:text-zinc-500 text-white rounded-xl transition-colors duration-200 cursor-pointer"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
          <div className="text-center mt-3">
            <p className="text-[11px] text-zinc-500">AI agents can make mistakes. Verify code executions.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
