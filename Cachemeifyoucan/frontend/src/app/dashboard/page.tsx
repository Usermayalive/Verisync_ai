"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import ChatArea from "@/components/ChatArea";
import RightPanel from "@/components/RightPanel";

export type Message = {
  id: number;
  role: "user" | "ai";
  content: string;
};

export type AuditData = {
  temporal_drift_warning: string | null;
  lightweight_judge_result: string;
  epistemic_judge_result: string | null;
  judge_reasoning: string | null;
  judge_confidence: number;
  max_similarity: number;
  real_chain: Record<string, unknown> | null;
  fake_chain: Record<string, unknown> | null;
  sources: { source: string; location: string; source_type?: string; language?: string }[];
  duplicate_sources: string[];
  pii_report: Record<string, unknown>[];
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "change-this-in-prod";

export default function Dashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isRightPanelOpen, setIsRightPanelOpen] = useState(false);
  const [auditData, setAuditData] = useState<AuditData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID());

  const handleNewChat = () => {
    setMessages([]);
    setAuditData(null);
    setIsRightPanelOpen(false);
    setSessionId(crypto.randomUUID());
  };

  // Session guard — redirect unauthenticated users to login
  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/");
    }
  }, [status, router]);

  // Show loading spinner while session resolves
  if (status === "loading" || status === "unauthenticated") {
    return (
      <div className="h-screen w-full bg-[#090E17] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#82B1FF] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }


  // Accept model as second argument
  const handleSendMessage = async (content: string, model: string) => {
    const newMessage: Message = { id: Date.now(), role: "user", content };
    const updatedMessages = [...messages, newMessage];
    setMessages(updatedMessages);
    setIsRightPanelOpen(true);
    setIsLoading(true);

    const chatHistory = updatedMessages.map(m => ({
      role: m.role === "user" ? "user" : "assistant",
      content: m.content,
    }));

    try {
      const res = await fetch(`${API_URL}/api/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": API_KEY,
        },
        body: JSON.stringify({ question: content, session_id: sessionId, chat_history: chatHistory, model }),
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`API Error ${res.status}: ${errText}`);
      }

      const data = await res.json();

      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: "ai",
        content: data.final_answer || "No answer generated.",
      }]);

      setAuditData({
        temporal_drift_warning: data.temporal_drift_warning,
        lightweight_judge_result: data.lightweight_judge_result,
        epistemic_judge_result: data.epistemic_judge_result,
        judge_reasoning: data.judge_reasoning,
        judge_confidence: data.judge_confidence,
        max_similarity: data.max_similarity,
        real_chain: data.real_chain,
        fake_chain: data.fake_chain,
        sources: data.sources || [],
        duplicate_sources: data.duplicate_sources || [],
        pii_report: data.pii_report || [],
      });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: "ai",
        content: `⚠️ Connection error: ${errorMessage}\n\nMake sure the FastAPI backend is running at ${API_URL}`,
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    const tempMessage: Message = { id: Date.now(), role: "user", content: `Uploading document: ${file.name}...` };
    setMessages(prev => [...prev, tempMessage]);
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("session_id", sessionId);

      const res = await fetch(`${API_URL}/api/ingest`, {
        method: "POST",
        headers: {
          "X-API-Key": API_KEY,
        },
        body: formData,
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`Upload Error ${res.status}: ${errText}`);
      }

      const data = await res.json();
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: "ai",
        content: `✅ Successfully ingested "${data.filename || file.name}". The RAG pipeline has completed vectorization and chunking. You can now ask questions about it.`,
      }]);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: "ai",
        content: `⚠️ Document upload failed: ${errorMessage}`,
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUrlIngest = async (url: string) => {
    const tempMessage: Message = { id: Date.now(), role: "user", content: `Ingesting URL: ${url}...` };
    setMessages(prev => [...prev, tempMessage]);
    setIsLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/ingest_url`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": API_KEY,
        },
        body: JSON.stringify({ url, session_id: sessionId }),
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`Ingest Error ${res.status}: ${errText}`);
      }

      const data = await res.json();
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: "ai",
        content: `✅ Successfully ingested content from "${data.url}". The RAG pipeline has completed parsing and indexing. You can now ask questions about it.`,
      }]);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: "ai",
        content: `⚠️ URL ingestion failed: ${errorMessage}`,
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <div 
      className={`h-screen w-full bg-[#090E17] font-sans tracking-wide overflow-hidden flex flex-col md:grid transition-all duration-300 ${
        hasMessages && isRightPanelOpen ? 'md:grid-cols-[auto_minmax(0,1fr)_360px]' : 'md:grid-cols-[auto_minmax(0,1fr)]'
      }`}
    >
      <Sidebar className="hidden md:flex" onNewChat={handleNewChat} />

      <ChatArea 
        className="flex-1 min-w-0" 
        messages={messages} 
        onSendMessage={handleSendMessage}
        onFileUpload={handleFileUpload}
        onUrlIngest={handleUrlIngest}
        isLoading={isLoading}
      />

      {hasMessages && isRightPanelOpen && (
        <div className="hidden lg:flex w-full h-full border-l border-[#222E40] bg-[#0D1522] animate-in slide-in-from-right-8 fade-in duration-500 overflow-hidden">
          <RightPanel 
            className="w-full border-none" 
            onClose={() => setIsRightPanelOpen(false)}
            auditData={auditData}
          />
        </div>
      )}
    </div>
  );
}
