"use client";

import { Send, Paperclip, Sparkles, Loader2, Link as LinkIcon } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { Message } from "@/app/dashboard/page";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const LOADING_MESSAGES = [
  "Running self-auditing pipeline...",
  "Searching strictly isolated vectors...",
  "Checking epistemic chains...",
  "Applying causal autopsy...",
  "Validating source integrity...",
  "Formulating verified answer..."
];

export default function ChatArea({ 
  messages, 
  onSendMessage, 
  onFileUpload,
  onUrlIngest,
  isLoading = false,
  className = "" 
}: { 
  messages: Message[], 
  onSendMessage: (msg: string, model: string) => void, 
  onFileUpload?: (file: File) => void,
  onUrlIngest?: (url: string) => void,
  isLoading?: boolean,
  className?: string 
}) {
  const [input, setInput] = useState("");
  const [urlInput, setUrlInput] = useState("");
  const [isUrlMode, setIsUrlMode] = useState(false);
  const [selectedModel, setSelectedModel] = useState("gemini");
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [loadingTextIndex, setLoadingTextIndex] = useState(0);
  
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isLoading) {
      interval = setInterval(() => {
        setLoadingTextIndex((prev) => (prev + 1) % LOADING_MESSAGES.length);
      }, 2000);
    } else {
      setLoadingTextIndex(0);
    }
    return () => clearInterval(interval);
  }, [isLoading]);
  
  const hasMessages = messages.length > 0;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onFileUpload) {
      onFileUpload(file);
    }
    if (e.target) {
      e.target.value = "";
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input, selectedModel);
      setInput("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  useEffect(() => {
    if (hasMessages) {
       endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, hasMessages]);

  const formContent = (
    <form onSubmit={handleSubmit} className="flex-1 flex max-w-[48rem] mx-auto w-full flex-col bg-[#151D2C] rounded-3xl border border-[#222E40] focus-within:border-[#33588D] focus-within:ring-2 focus-within:ring-[#132A4B]/50 transition-all shadow-lg overflow-hidden">
        <div className="flex items-center gap-3 px-4 pt-4">
          <label htmlFor="model-select" className="text-xs text-[#94A3B8]">Model:</label>
          <select
            id="model-select"
            value={selectedModel}
            onChange={e => setSelectedModel(e.target.value)}
            className="bg-[#0D1522] border border-[#222E40] text-[#E2E8F0] text-xs rounded-lg px-2 py-1 focus:outline-none"
            disabled={isLoading}
          >
            <option value="gemini">Gemini</option>
            <option value="deepseek">DeepSeek</option>
          </select>
        </div>
        {isUrlMode ? (
          <div className="flex items-center px-4 py-4 gap-3 bg-[#0D1522] border-b border-[#222E40]">
            <LinkIcon className="w-4 h-4 text-[#82B1FF]" />
            <input 
              type="url"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="Paste YouTube or Web URL here..."
              className="flex-1 bg-transparent border-none focus:outline-none text-[#E2E8F0] placeholder-[#64748B] text-sm"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  if (urlInput.trim() && onUrlIngest) {
                    onUrlIngest(urlInput);
                    setUrlInput("");
                    setIsUrlMode(false);
                  }
                }
                if (e.key === 'Escape') setIsUrlMode(false);
              }}
              autoFocus
            />
            <button 
              type="button"
              onClick={() => {
                if (urlInput.trim() && onUrlIngest) {
                  onUrlIngest(urlInput);
                  setUrlInput("");
                  setIsUrlMode(false);
                }
              }}
              className="px-3 py-1 bg-[#82B1FF] text-[#090E17] text-xs font-bold rounded-lg hover:bg-white transition-all"
            >
              Add
            </button>
          </div>
        ) : null}
        <textarea 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          onKeyDown={handleKeyDown}
          placeholder="Ask about your ingested documents..." 
          className="w-full bg-transparent border-none focus:outline-none text-[#E2E8F0] placeholder-[#64748B] px-5 py-4 resize-none min-h-[56px] max-h-[200px]"
          rows={1}
          disabled={isLoading}
        />
        <div className="flex items-center justify-between px-3 pb-3">
          <div className="flex items-center gap-1">
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange}
              className="hidden" 
              accept=".pdf,.txt,.csv,.md,.jpg,.png,.jpeg,.mp3,.wav" 
            />
            <button 
              type="button" 
              disabled={isLoading}
              onClick={() => fileInputRef.current?.click()}
              className="p-2 text-[#64748B] hover:text-[#E2E8F0] rounded-xl hover:bg-[#1E293B] disabled:opacity-50 transition-colors"
              title="Upload File"
            >
              <Paperclip className="w-5 h-5" />
            </button>
            <button 
              type="button" 
              disabled={isLoading}
              onClick={() => setIsUrlMode(!isUrlMode)}
              className={`p-2 rounded-xl transition-colors ${isUrlMode ? 'text-[#82B1FF] bg-[#1E293B]' : 'text-[#64748B] hover:text-[#E2E8F0] hover:bg-[#1E293B]'}`}
              title="Add URL"
            >
              <LinkIcon className="w-5 h-5" />
            </button>
          </div>
          <button type="submit" disabled={!input.trim() || isLoading} className="p-2 bg-[#E2E8F0] disabled:bg-transparent disabled:text-[#334155] text-[#090E17] rounded-full hover:bg-white transition-all">
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </div>
    </form>
  );

  return (
    <div className={`flex flex-col h-full bg-[#090E17] relative overflow-hidden ${className}`}>
      {!hasMessages ? (
        <div className="flex-1 flex flex-col items-center justify-center p-6 relative">
          <div className="flex flex-col items-center mb-8">
            <div className="w-16 h-16 bg-[#0D1522] border border-[#222E40] text-[#E2E8F0] rounded-3xl shadow-[0_4px_12px_rgb(0,0,0,0.2)] flex items-center justify-center mb-8">
              <Sparkles className="w-8 h-8" />
            </div>
            <h2 className="text-[32px] font-medium text-[#E2E8F0] tracking-tight">Ask anything. Trust every answer.</h2>
            <p className="text-[15px] text-[#64748B] mt-2 max-w-md text-center">Powered by a three-layer self-auditing pipeline that adversarially tests its own reasoning.</p>
          </div>
          
          <div className="w-full flex px-4">
             {formContent}
          </div>
          
          <div className="flex flex-wrap justify-center gap-3 mt-8 max-w-3xl text-[13px] font-medium">
            <button onClick={() => setInput("What is the main finding of the research paper?")} className="px-4 py-2.5 rounded-2xl bg-[#0D1522] border border-[#222E40] text-[#94A3B8] hover:text-[#E2E8F0] hover:bg-[#1E293B] transition-all">📄 Research findings</button>
            <button onClick={() => setInput("What is the value in Table 2, row 3?")} className="px-4 py-2.5 rounded-2xl bg-[#0D1522] border border-[#222E40] text-[#94A3B8] hover:text-[#E2E8F0] hover:bg-[#1E293B] transition-all">📊 Table extraction</button>
            <button onClick={() => setInput("Compare the 2021 podcast and 2023 paper.")} className="px-4 py-2.5 rounded-2xl bg-[#0D1522] border border-[#222E40] text-[#94A3B8] hover:text-[#E2E8F0] hover:bg-[#1E293B] transition-all">⏳ Temporal drift</button>
            <button onClick={() => setInput("What is the capital of Australia?")} className="px-4 py-2.5 rounded-2xl bg-[#0D1522] border border-[#222E40] text-[#94A3B8] hover:text-[#E2E8F0] hover:bg-[#1E293B] transition-all">🚫 Out-of-corpus test</button>
          </div>
        </div>
      ) : (
        <>
          <div className="flex-1 overflow-y-auto px-4 md:px-12 py-8 space-y-8 scroll-smooth">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex max-w-[48rem] mx-auto w-full group ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                
                {msg.role === 'ai' && (
                  <div className="w-8 h-8 rounded-full bg-[#151D2C] border border-[#222E40] text-[#E2E8F0] flex items-center justify-center shrink-0 mr-4 mt-1 shadow-sm">
                     <Sparkles className="w-4 h-4" />
                  </div>
                )}

                <div 
                  className={`text-[15px] leading-relaxed max-w-[85%] ${
                    msg.role === 'user' 
                      ? 'bg-[#1E293B] text-[#E2E8F0] rounded-[24px] rounded-br-sm px-5 py-3 shadow-md whitespace-pre-wrap' 
                      : 'bg-transparent text-[#E2E8F0] px-1 py-1 w-full'
                  }`}
                >
                  {msg.role === 'user' ? (
                    msg.content
                  ) : (
                    <ReactMarkdown 
                      remarkPlugins={[remarkGfm]}
                      components={{
                        p: ({node, ...props}) => <p className="mb-4 last:mb-0 leading-relaxed" {...props} />,
                        ul: ({node, ...props}) => <ul className="list-disc list-outside ml-5 mb-4 space-y-1 text-[#94A3B8]" {...props} />,
                        ol: ({node, ...props}) => <ol className="list-decimal list-outside ml-5 mb-4 space-y-1 text-[#94A3B8]" {...props} />,
                        li: ({node, ...props}) => <li className="pl-1" {...props} />,
                        strong: ({node, ...props}) => <strong className="font-semibold text-white" {...props} />,
                        h3: ({node, ...props}) => <h3 className="text-lg font-semibold mt-6 mb-3 text-white" {...props} />,
                        h4: ({node, ...props}) => <h4 className="text-base font-medium mt-4 mb-2 text-white" {...props} />,
                        blockquote: ({node, ...props}) => <blockquote className="border-l-2 border-[#33588D] pl-4 italic text-[#94A3B8] my-4 bg-[#151D2C]/50 rounded-r-lg py-2" {...props} />,
                        table: ({node, ...props}) => <div className="overflow-x-auto my-6 border border-[#222E40] rounded-xl"><table className="w-full text-sm text-left" {...props} /></div>,
                        thead: ({node, ...props}) => <thead className="text-xs text-[#94A3B8] uppercase bg-[#151D2C] border-b border-[#222E40]" {...props} />,
                        th: ({node, ...props}) => <th className="px-4 py-3 font-semibold" {...props} />,
                        td: ({node, ...props}) => <td className="px-4 py-3 border-b border-[#222E40]/50" {...props} />,
                        a: ({node, ...props}) => (
                          <a {...props} target="_blank" rel="noopener noreferrer" className="text-[#82B1FF] hover:text-white underline underline-offset-2 decoration-[#33588D] transition-colors font-medium">
                            {props.children}
                          </a>
                        ),
                        // @ts-ignore
                        code: ({node, inline, ...props}) => (
                          inline 
                            ? <code className="bg-[#151D2C] text-[#82B1FF] px-1.5 py-0.5 rounded-md text-[13px] font-mono border border-[#222E40]" {...props} />
                            : <pre className="bg-[#0D1522] border border-[#222E40] rounded-xl p-4 overflow-x-auto my-4 text-[13px] font-mono leading-relaxed"><code {...props} /></pre>
                        )
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex max-w-[48rem] mx-auto w-full justify-start">
                <div className="w-8 h-8 rounded-full bg-[#151D2C] border border-[#222E40] text-[#82B1FF] flex items-center justify-center shrink-0 mr-4 mt-1 shadow-sm">
                  <Loader2 className="w-4 h-4 animate-spin" />
                </div>
                <div className="text-[15px] text-[#64748B] italic px-1 py-2 animate-pulse">{LOADING_MESSAGES[loadingTextIndex]}</div>
              </div>
            )}
            <div ref={endOfMessagesRef} className="h-4" />
          </div>
          
          <div className="p-4 pt-0 w-full flex justify-center bg-gradient-to-t from-[#090E17] via-[#090E17]/95 to-transparent">
             <div className="max-w-[48rem] w-full">
               {formContent}
               <div className="text-center mt-3 text-[11px] text-[#64748B]">
                 VeriSync_ai — Provably grounded answers with adversarial self-auditing.
               </div>
             </div>
          </div>
        </>
      )}
    </div>
  );
}
