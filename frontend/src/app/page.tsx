"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

type Message = {
  id: string;
  role: "user" | "agent";
  content: string;
  status: "processing" | "completed" | "failed";
  trace?: string[];
  docsCount?: number;
  retries?: number;
  timeTaken?: number;
};

// Helper to map backend trace strings to beautiful UI elements
const parseTraceMessage = (msg: string) => {
  if (msg.startsWith("Orchestrator (Retry)")) return { icon: "🔄", label: "Agent Orchestrator", text: msg.replace("Orchestrator (Retry):", "").trim(), color: "text-orange-400" };
  if (msg.startsWith("Orchestrator")) return { icon: "🧠", label: "Agent Orchestrator", text: msg.replace("Orchestrator:", "").trim(), color: "text-indigo-400" };
  if (msg.startsWith("Retriever")) return { icon: "🔍", label: "Data Retriever", text: msg.replace("Retriever:", "").trim(), color: "text-blue-400" };
  if (msg.startsWith("Reranker")) return { icon: "⚖️", label: "Cross-Encoder Reranker", text: msg.replace("Reranker:", "").trim(), color: "text-purple-400" };
  if (msg.startsWith("Validator")) return { icon: "🛡️", label: "Context Validator", text: msg.replace("Validator:", "").trim(), color: "text-rose-400" };
  if (msg.startsWith("Summarizer")) return { icon: "✍️", label: "Synthesis Engine", text: msg.replace("Summarizer:", "").trim(), color: "text-emerald-400" };
  if (msg.startsWith("Web Search")) return { icon: "🌐", label: "Web Search Agent", text: msg.replace("Web Search Agent:", "").trim(), color: "text-blue-500" };
  return { icon: "⚙️", label: "System", text: msg, color: "text-slate-400" };
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [useWebSearch, setUseWebSearch] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const pollStatus = async (queryId: string, msgId: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/status/${queryId}`);
        const data = await res.json();
        
        if (data.status === "processing") {
           if (data.trace && data.trace.length > 0) {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === msgId ? { ...msg, trace: data.trace } : msg
                )
              );
           }
        } else if (data.status === "completed" || data.status === "failed") {
          clearInterval(interval);
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === msgId
                ? {
                    ...msg,
                    status: data.status,
                    content: data.result?.final_answer || (data.status === "failed" ? data.error || "Error generating response." : ""),
                    trace: data.result?.reasoning_trace || data.trace,
                    docsCount: data.result?.retrieved_docs_count,
                    retries: data.result?.retries,
                    timeTaken: data.result?.time_taken,
                  }
                : msg
            )
          );
        }
      } catch (e) {
        console.error("Polling error", e);
      }
    }, 2000);
  };

  const handlesubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = { id: Date.now().toString(), role: "user", content: input, status: "completed" };
    const agentMsgId = (Date.now() + 1).toString();
    const agentMsg: Message = { id: agentMsgId, role: "agent", content: "", status: "processing" };

    setMessages((prev) => [...prev, userMsg, agentMsg]);
    setInput("");

    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMsg.content, user_id: "user_123", use_web_search: useWebSearch }),
      });
      const data = await res.json();
      
      if (data.query_id) {
        pollStatus(data.query_id, agentMsgId);
      }
    } catch (e) {
      setMessages((prev) =>
        prev.map((msg) => (msg.id === agentMsgId ? { ...msg, status: "failed", content: "Failed to connect to server." } : msg))
      );
    }
  };

  return (
    <main className="flex flex-col h-screen w-full bg-[#0B1120] text-slate-100 font-sans selection:bg-teal-500/30 overflow-hidden">
      
      {/* Safely bound dynamic backgrounds to avoid horizontal scrolling */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] bg-teal-500/10 rounded-full blur-[120px]" />
        <div className="absolute -bottom-[20%] -right-[10%] w-[50%] h-[50%] bg-indigo-500/10 rounded-full blur-[120px]" />
      </div>

      {/* Header - Fixed Height */}
      <header className="relative z-10 flex-none h-16 px-4 md:px-6 border-b border-slate-700/80 bg-slate-900 shadow-sm flex items-center justify-between">
        <div className="w-full max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
             <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-teal-500/20">
                <span className="text-white font-bold text-lg leading-none">L</span>
             </div>
             <div>
                <h1 className="text-xl font-bold text-slate-100 tracking-wide">
                  LangGraph <span className="text-teal-400 font-medium ml-0.5">Agents</span>
                </h1>
             </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="px-3 py-1.5 rounded-md bg-slate-800 border border-slate-600 flex items-center space-x-2 shadow-inner">
               <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-teal-500"></span>
               </span>
               <span className="text-xs font-semibold text-slate-300 tracking-wider uppercase hidden sm:inline-block">Connected</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Chat Scrollable Area - Using min-h-0 to prevent flex blowout */}
      <div className="relative z-10 flex-1 min-h-0 overflow-y-auto p-4 md:p-8 scroll-smooth flex flex-col items-center">
        <div className="w-full max-w-4xl space-y-8 pb-4">
          
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-[60vh] text-slate-400 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <div className="p-6 md:p-8 w-full max-w-lg rounded-3xl bg-slate-800/30 border border-slate-700/50 backdrop-blur-md shadow-2xl flex flex-col items-center text-center mx-4">
                <div className="w-16 h-16 mb-6 rounded-full bg-gradient-to-br from-teal-500/20 to-emerald-500/20 flex items-center justify-center border border-teal-500/30 shadow-[0_0_30px_rgba(45,212,191,0.2)]">
                  <svg className="w-8 h-8 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                </div>
                <h2 className="text-2xl font-bold text-slate-100 mb-3 tracking-wide">Initiate Workflow</h2>
                <p className="text-sm text-slate-400 leading-relaxed mb-8 px-4">
                  Ask a complex question. The orchestrator will dynamically delegate tasks to specialized retrieval, reasoning, and validation agents.
                </p>
                <div className="flex flex-col space-y-3 w-full">
                  <button onClick={() => setInput("Summarize GDPR Article 32 and how it applies to breach cases.")} className="text-left w-full p-4 rounded-xl border border-slate-700/80 bg-slate-800/40 hover:bg-slate-700/60 hover:border-teal-500/50 transition-all duration-300 group text-sm font-medium text-slate-300">
                    <span className="text-teal-400 mr-2 group-hover:translate-x-1 inline-block transition-transform">→</span>
                    Summarize GDPR Article 32 regarding breach cases.
                  </button>
                  <button onClick={() => setInput("What are the main causes of OAuth token leakage and mitigations?")} className="text-left w-full p-4 rounded-xl border border-slate-700/80 bg-slate-800/40 hover:bg-slate-700/60 hover:border-teal-500/50 transition-all duration-300 group text-sm font-medium text-slate-300">
                    <span className="text-teal-400 mr-2 group-hover:translate-x-1 inline-block transition-transform">→</span>
                    Causes of OAuth token leakage and mitigations?
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {messages.map((msg) => (
            <div key={msg.id} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"} animate-in fade-in slide-in-from-bottom-2 duration-500`}>
              <div
                className={`max-w-[95%] sm:max-w-[85%] md:max-w-[75%] p-5 sm:p-6 rounded-3xl shadow-xl ${
                  msg.role === "user" 
                    ? "bg-gradient-to-br from-teal-500 to-emerald-600 text-white rounded-br-sm border border-teal-400/30 shadow-teal-500/20" 
                    : "bg-[#151D2E] border border-slate-700/60 text-slate-200 rounded-bl-sm backdrop-blur-xl"
                }`}
              >
                {msg.role === "agent" && msg.status === "processing" ? (
                  <div className="flex flex-col space-y-5">
                    <div className="flex items-center space-x-3 text-teal-400 font-medium">
                       <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-teal-500"></span>
                      </span>
                      <span className="tracking-wide animate-pulse">Agents Orchestrating...</span>
                    </div>
                    {msg.trace && msg.trace.length > 0 && (
                      <div className="p-4 bg-[#0B1120] rounded-2xl flex flex-col space-y-3 border border-slate-700/50 shadow-inner overflow-hidden">
                         {msg.trace.map((step, i) => {
                            const parsed = parseTraceMessage(step);
                            return (
                              <div key={i} className="flex items-start text-sm animate-in fade-in slide-in-from-left-2 duration-300 overflow-hidden">
                                <span className="mr-3 text-lg flex-shrink-0">{parsed.icon}</span>
                                <div className="flex flex-col min-w-0">
                                  <span className={`font-semibold text-xs uppercase tracking-wider ${parsed.color} mb-0.5 truncate`}>{parsed.label}</span>
                                  <span className="text-slate-300 leading-snug break-words">{parsed.text}</span>
                                </div>
                              </div>
                            )
                         })}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-col space-y-4">
                    <div className="prose prose-invert prose-emerald prose-p:leading-relaxed prose-pre:bg-[#0B1120] prose-pre:border prose-pre:border-slate-800 max-w-none text-[15px] break-words">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                    
                    {msg.trace && msg.trace.length > 0 && (
                      <div className="mt-6 pt-4 border-t border-slate-700/50">
                        <details className="group cursor-pointer">
                          <summary className="text-xs font-semibold text-slate-400 select-none flex items-center hover:text-teal-400 transition-colors list-none outline-none">
                            <span className="mr-2">View Reasoning Trace</span>
                            <span className="group-open:rotate-180 transition-transform text-slate-500">▼</span>
                          </summary>
                          <div className="mt-3 p-4 bg-[#0B1120]/80 rounded-2xl flex flex-col space-y-3 border border-slate-800 shadow-inner overflow-hidden">
                             {msg.trace.map((step, i) => {
                                const parsed = parseTraceMessage(step);
                                return (
                                  <div key={i} className="flex items-start text-sm">
                                    <span className="mr-3 text-lg opacity-80 flex-shrink-0">{parsed.icon}</span>
                                    <div className="flex flex-col min-w-0">
                                      <span className={`font-semibold text-[10px] uppercase tracking-wider ${parsed.color} opacity-80 mb-0.5 truncate`}>{parsed.label}</span>
                                      <span className="text-slate-400 leading-snug text-[13px] break-words">{parsed.text}</span>
                                    </div>
                                  </div>
                                )
                             })}
                             {msg.docsCount !== undefined && (
                               <div className="pt-3 mt-1 border-t border-slate-800 flex justify-between items-center text-[11px] text-slate-500 font-medium uppercase tracking-wider truncate">
                                 <span className="flex space-x-3">
                                   <span>Retrieved: {msg.docsCount} Chunks</span>
                                   {msg.timeTaken !== undefined && <span>Time: {msg.timeTaken}s</span>}
                                 </span>
                                 <span>Retries: {msg.retries}</span>
                               </div>
                             )}
                          </div>
                        </details>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={endRef} className="h-4 w-full flex-none" />
        </div>
      </div>

      {/* Footer Area - Fixed Height */}
      <div className="relative z-10 flex-none p-4 md:p-6 bg-slate-900 border-t border-slate-800/60 shadow-[0_-10px_40px_rgba(0,0,0,0.2)]">
        <form onSubmit={handlesubmit} className="w-full max-w-4xl mx-auto flex sm:flex-row flex-col sm:items-stretch space-y-3 sm:space-y-0 sm:space-x-3">
          
          <label className="flex flex-shrink-0 items-center justify-center space-x-3 cursor-pointer group select-none whitespace-nowrap bg-[#151D2E] hover:bg-slate-800 px-5 py-3 sm:py-0 rounded-xl transition-all border border-slate-700/80 shadow-inner">
            <div className="relative inline-flex items-center">
              <input type="checkbox" className="sr-only" checked={useWebSearch} onChange={(e) => setUseWebSearch(e.target.checked)} />
              <div className={`block w-11 h-6 rounded-full transition-colors duration-300 ease-in-out border ${useWebSearch ? 'bg-teal-500 border-teal-500' : 'bg-slate-700 border-slate-600'}`}></div>
              <div className={`dot absolute left-[3px] top-[3px] bg-white w-[18px] h-[18px] rounded-full transition-transform duration-300 ease-in-out shadow-sm ${useWebSearch ? 'translate-x-5' : 'translate-x-0'}`}></div>
            </div>
            <span className={`text-[13px] font-bold tracking-wide transition-colors ${useWebSearch ? 'text-teal-400' : 'text-slate-400 group-hover:text-slate-300'}`}>
              WEB SEARCH
            </span>
          </label>

          <div className="relative flex-1 w-full flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Command your agent..."
              className="w-full h-full bg-[#151D2E] border border-slate-700/80 rounded-xl pl-6 pr-28 py-3.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50 transition-all shadow-inner text-[15px]"
            />
            <button
              type="submit"
              disabled={!input.trim()}
              className="absolute right-2 top-2 bottom-2 px-6 bg-teal-500 hover:bg-teal-400 text-slate-900 font-bold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-[0_0_15px_rgba(45,212,191,0.4)] hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center"
            >
              Send
            </button>
          </div>

          <button
            type="button"
            onClick={() => setMessages([])}
            disabled={messages.length === 0}
            title="Clear Chat"
            className="hidden sm:flex items-center justify-center px-4 rounded-xl bg-[#151D2E] hover:bg-rose-500/10 text-slate-400 hover:text-rose-400 border border-slate-700/80 hover:border-rose-500/30 transition-all disabled:opacity-0 disabled:pointer-events-none hover:shadow-lg"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </form>
      </div>

    </main>
  );
}
