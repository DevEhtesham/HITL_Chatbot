"use client";

import React, { useState, useRef, useEffect } from "react";
import ActionCard from "../components/ActionCard";

interface Message {
  role: "user" | "bot";
  content: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [pendingAction, setPendingAction] = useState<{toolName: string, toolArgs: any} | null>(null);
  const [isMounted, setIsMounted] = useState(false);
  const threadId = useRef(`thread_${Math.random().toString(36).substring(7)}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, pendingAction]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setIsLoading(true);
    setPendingAction(null);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg, thread_id: threadId.current })
      });
      const data = await res.json();
      console.log("DEBUG - Chat response:", data);
      
      if (data.status === "pending_approval") {
        setMessages(prev => [...prev, { role: "bot", content: "I need to perform an action." }]);
        setPendingAction({ toolName: data.pending_tool, toolArgs: data.tool_args });
      } else {
        setMessages(prev => [...prev, { role: "bot", content: data.response }]);
      }
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: "bot", content: "An error occurred while communicating with the backend." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAction = async (action: "approve" | "reject") => {
    setIsLoading(true);
    setPendingAction(null);
    try {
      const res = await fetch("http://localhost:8000/api/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: action, thread_id: threadId.current })
      });
      const data = await res.json();
      console.log("DEBUG - Action response:", data);
      setMessages(prev => [...prev, { role: "bot", content: data.response }]);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const resetChat = () => {
    setMessages([]);
    setPendingAction(null);
    threadId.current = `thread_${Math.random().toString(36).substring(7)}`;
  };

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-100 font-sans">
      <header className="py-4 px-6 border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm flex justify-between items-center sticky top-0 z-10">
        <div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">HITL Chatbot</h1>
          <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Memory-Enabled Assistant</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="hidden md:block text-right">
            <p className="text-[10px] text-gray-500 uppercase font-bold">Current Thread</p>
            <p className="text-xs text-blue-400 font-mono">{isMounted ? threadId.current : "..."}</p>
          </div>
          <button 
            onClick={resetChat}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors group"
            title="Start New Chat"
          >
            <svg className="w-5 h-5 text-gray-400 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scrollbar-hide">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl flex items-center justify-center shadow-2xl shadow-blue-500/20 rotate-3 transition-transform hover:rotate-0">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Advanced HITL Chatbot</h2>
              <p className="text-gray-400 max-w-sm mx-auto">
                Securely crawl GitHub repositories and LinkedIn profiles with human-in-the-loop approval.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-xl">
              {/* <button 
                onClick={() => setInput("Crawl the langchain-ai/langgraph repo")}
                className="p-4 bg-gray-900 border border-gray-800 rounded-2xl text-left hover:border-blue-500/50 transition-all"
              >
                <p className="text-blue-400 text-xs font-bold uppercase mb-1">GitHub</p>
                <p className="text-sm text-gray-300">Crawl a repository and summarize its README.</p>
              </button>
              <button 
                onClick={() => setInput("Summarize this LinkedIn profile: https://linkedin.com/in/...")}
                className="p-4 bg-gray-900 border border-gray-800 rounded-2xl text-left hover:border-blue-500/50 transition-all"
              >
                <p className="text-blue-400 text-xs font-bold uppercase mb-1">LinkedIn</p>
                <p className="text-sm text-gray-300">Get details from a professional profile.</p>
              </button> */}
            </div>
          </div>
        )}

        <div className="max-w-3xl mx-auto space-y-6 pb-20">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start animate-in fade-in slide-in-from-bottom-2"}`}>
              <div 
                className={`max-w-[85%] rounded-2xl p-4 whitespace-pre-wrap leading-relaxed shadow-sm ${
                  msg.role === "user" 
                    ? "bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-tr-none" 
                    : "bg-gray-800 text-gray-100 rounded-tl-none border border-gray-700"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}

          {pendingAction && (
            <div className="flex justify-start animate-in zoom-in-95 duration-300">
              <ActionCard 
                toolName={pendingAction.toolName} 
                toolArgs={pendingAction.toolArgs}
                onApprove={() => handleAction("approve")}
                onReject={() => handleAction("reject")}
              />
            </div>
          )}

          {isLoading && !pendingAction && (
            <div className="flex justify-start">
              <div className="bg-gray-800 border border-gray-700 rounded-2xl rounded-tl-none p-4 flex items-center space-x-2">
                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse"></div>
                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse delay-75"></div>
                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse delay-150"></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="p-4 border-t border-gray-800 bg-gray-900/50 backdrop-blur-xl">
        <form onSubmit={sendMessage} className="max-w-3xl mx-auto relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading || pendingAction !== null}
            placeholder={pendingAction ? "Action pending approval..." : "Type your message..."}
            className="w-full bg-gray-900/50 border border-gray-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-2xl py-4 pl-6 pr-14 text-white placeholder-gray-500 outline-none transition-all disabled:opacity-50"
          />
          <button 
            type="submit" 
            disabled={!input.trim() || isLoading || pendingAction !== null}
            className="absolute right-3 p-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl disabled:opacity-50 transition-all hover:scale-105 active:scale-95"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </form>
      </footer>
    </div>
  );
}
