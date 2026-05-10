"use client";

import { ResponsivePie } from "@nivo/pie";
import { FileText, Clock, Shield, ShieldAlert, AlertTriangle, CheckCircle2, XCircle, ChevronDown, ChevronRight, X, PlaySquare, BookOpen, ExternalLink, Play, Table2, Database, Globe } from "lucide-react";
import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { AuditData } from "@/app/dashboard/page";

const SOURCE_TYPE_COLORS: Record<string, string> = {
  PDF: "#3B82F6",
  CSV: "#10B981",
  MP3: "#F59E0B",
  YouTube: "#EF4444",
  Image: "#8B5CF6",
  Unknown: "#64748B",
};

function buildPieData(sources: { source: string; source_type?: string }[]) {
  const counts: Record<string, number> = {};
  for (const s of sources) {
    const t = s.source_type || guessType(s.source);
    counts[t] = (counts[t] || 0) + 1;
  }
  return Object.entries(counts).map(([id, value]) => ({
    id,
    label: id,
    value,
    color: SOURCE_TYPE_COLORS[id] || SOURCE_TYPE_COLORS.Unknown,
  }));
}

function guessType(name: string): string {
  const ext = name.split(".").pop()?.toLowerCase();
  if (ext === "pdf") return "PDF";
  if (ext === "csv") return "CSV";
  if (ext === "mp3" || ext === "wav") return "MP3";
  if (ext === "png" || ext === "jpg" || ext === "jpeg") return "Image";
  if (name.includes("youtube") || name.includes("youtu.be")) return "YouTube";
  return "PDF";
}

function getIcon(type: string) {
  switch (type) {
    case "PDF": return <FileText className="w-4 h-4 text-blue-400" />;
    case "CSV": return <Table2 className="w-4 h-4 text-emerald-400" />;
    case "MP3": return <Play className="w-4 h-4 text-amber-400" />;
    case "YouTube": return <PlaySquare className="w-4 h-4 text-red-400" />;
    case "Image": return <BookOpen className="w-4 h-4 text-purple-400" />;
    default: return <ExternalLink className="w-4 h-4 text-slate-400" />;
  }
}

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = pct >= 70 ? "bg-emerald-500" : pct >= 40 ? "bg-amber-500" : "bg-rose-500";
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-2 bg-[#1E293B] rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all duration-700`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-semibold text-[#E2E8F0] tabular-nums">{pct}%</span>
    </div>
  );
}

function CollapsibleSection({ title, icon, children, defaultOpen = false, badge }: { title: string; icon: React.ReactNode; children: React.ReactNode; defaultOpen?: boolean; badge?: string }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-[#222E40] rounded-2xl overflow-hidden">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center gap-3 px-4 py-3 hover:bg-[#151D2C] transition-colors text-left">
        {icon}
        <span className="text-sm font-medium text-[#E2E8F0] flex-1">{title}</span>
        {badge && <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#132A4B] text-[#82B1FF]">{badge}</span>}
        {open ? <ChevronDown className="w-4 h-4 text-[#64748B]" /> : <ChevronRight className="w-4 h-4 text-[#64748B]" />}
      </button>
      {open && <div className="px-4 pb-4 text-sm text-[#94A3B8] space-y-2">{children}</div>}
    </div>
  );
}

export default function RightPanel({ className = "", onClose, auditData }: { className?: string; onClose?: () => void; auditData: AuditData | null }) {
  const [activeRef, setActiveRef] = useState<number | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  if (!auditData) {
    return (
      <div className={`flex flex-col h-full bg-[#0D1522] p-5 items-center justify-center ${className}`}>
        <Shield className="w-10 h-10 text-[#334155] mb-3" />
        <p className="text-sm text-[#64748B] text-center">Audit data will appear here after your first query.</p>
      </div>
    );
  }

  const pieData = buildPieData(auditData.sources);
  const judgeBadge = auditData.lightweight_judge_result === "SUFFICIENT" ? "Direct" : auditData.lightweight_judge_result === "AMBIGUOUS" ? "Audited" : "Refused";

  const uniqueRefs = auditData.sources.filter(
    (s, i, arr) => arr.findIndex(x => x.source === s.source) === i
  );

  return (
    <div className={`flex flex-col h-full bg-[#0D1522] border-l border-[#222E40] overflow-y-auto ${className}`}>
      <div className="p-5 space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-semibold text-[#64748B] uppercase tracking-widest">Audit Trail</h3>
          {onClose && (
            <button onClick={onClose} className="p-1.5 text-[#64748B] hover:text-[#E2E8F0] hover:bg-[#151D2C] rounded-lg transition-colors">
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
        {/* Project Knowledge Section (Re-implemented) */}
        {auditData?.source_manifest && auditData.source_manifest.length > 0 && (
          <div className="bg-[#151D2C] rounded-2xl border border-[#222E40] overflow-hidden">
            <div className="px-4 py-3 border-b border-[#222E40] bg-[#1a2333] flex items-center gap-2">
              <Database className="w-3.5 h-3.5 text-[#82B1FF]" />
              <h4 className="text-[10px] font-bold text-[#64748B] uppercase tracking-wider">Loaded Knowledge</h4>
            </div>
            <div className="p-2 max-h-48 overflow-y-auto space-y-1 custom-scrollbar">
              {auditData.source_manifest.map((src, idx) => {
                const isYoutube = src.includes("youtube.com") || src.includes("youtu.be");
                const isPdf = src.toLowerCase().endsWith(".pdf");
                
                return (
                  <div key={idx} className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-[#1a2333] transition-colors group">
                    {isYoutube ? <PlaySquare className="w-3.5 h-3.5 text-rose-400" /> : 
                     isPdf ? <FileText className="w-3.5 h-3.5 text-blue-400" /> : 
                     <Globe className="w-3.5 h-3.5 text-emerald-400" />}
                    <span className="text-[11px] text-[#94A3B8] truncate flex-1 group-hover:text-[#E2E8F0]">
                      {src.replace(/^https?:\/\/(www\.)?/, '')}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
        {/* Pie Chart — Source Type Distribution */}
        {pieData.length > 0 && (
          <div className="bg-[#151D2C] rounded-2xl border border-[#222E40] p-4">
            <h4 className="text-[10px] font-semibold text-[#64748B] uppercase tracking-wider mb-2">Source Match Distribution</h4>
            <div className="h-48 w-full -ml-1">
              <ResponsivePie
                data={pieData}
                margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
                innerRadius={0.6}
                padAngle={3}
                cornerRadius={6}
                activeOuterRadiusOffset={6}
                colors={{ datum: "data.color" }}
                borderWidth={1}
                borderColor={{ from: "color", modifiers: [["darker", 0.2]] }}
                enableArcLinkLabels={false}
                arcLabelsSkipAngle={10}
                arcLabelsTextColor="#ffffff"
                theme={{
                  tooltip: {
                    container: {
                      background: "#151D2C",
                      color: "#E2E8F0",
                      fontSize: 12,
                      borderRadius: 8,
                      boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.5)",
                    },
                  },
                }}
              />
            </div>
            <div className="flex flex-wrap gap-3 mt-3 justify-center">
              {pieData.map((d) => (
                <div key={d.id} className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                  <span className="text-[11px] text-[#94A3B8] font-medium">{d.id} ({d.value})</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Pipeline Route & Confidence */}
        <div className="bg-[#151D2C] rounded-2xl p-4 space-y-3 border border-[#222E40]">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">Pipeline Route</span>
            <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full ${
              judgeBadge === "Direct" ? "bg-emerald-500/10 text-emerald-400" :
              judgeBadge === "Audited" ? "bg-amber-500/10 text-amber-400" :
              "bg-rose-500/10 text-rose-400"
            }`}>{judgeBadge}</span>
          </div>
          <div className="text-xs text-[#94A3B8]">
            Lightweight Judge → <span className="text-[#E2E8F0] font-medium">{auditData.lightweight_judge_result}</span>
          </div>
          {auditData.epistemic_judge_result && (
            <div className="text-xs text-[#94A3B8]">
              Epistemic Judge → <span className="text-[#E2E8F0] font-medium">{auditData.epistemic_judge_result === "REAL" ? "✅ Real Chain Identified" : "❌ Failed to Identify"}</span>
            </div>
          )}
          <div className="pt-1">
            <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-1 block">Confidence</span>
            <ConfidenceBar value={auditData.judge_confidence} />
          </div>
        </div>

        {/* Temporal Drift Warning */}
        {auditData.temporal_drift_warning && (
          <div className="flex items-start gap-3 bg-amber-500/5 border border-amber-500/20 rounded-2xl p-4">
            <Clock className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-1">Temporal Drift</p>
              <p className="text-sm text-[#E2E8F0]">{auditData.temporal_drift_warning}</p>
            </div>
          </div>
        )}

        {/* References in Document — clickable cards */}
        <div>
          <h4 className="text-xs font-semibold text-[#64748B] uppercase tracking-widest mb-3">References in Document</h4>
          <div className="space-y-2">
            {uniqueRefs.map((ref, i) => {
              const sType = ref.source_type || guessType(ref.source);
              return (
                <button
                  key={i}
                  onClick={() => setActiveRef(i)}
                  className="w-full flex items-center justify-between p-3 rounded-xl border border-[#222E40] hover:border-[#33588D] hover:bg-[#132A4B]/50 transition-all group text-left"
                >
                  <div className="flex items-center gap-3 truncate">
                    <div className="p-1.5 bg-[#151D2C] rounded-lg group-hover:bg-[#1E293B] transition-colors">
                      {getIcon(sType)}
                    </div>
                    <div className="truncate">
                      <span className="text-sm text-[#E2E8F0] font-medium truncate block">{ref.source}</span>
                      <span className="text-[10px] text-[#64748B]">{ref.location}</span>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Evidence Chains */}
        {auditData.real_chain && (
          <CollapsibleSection title="Real Evidence Chain" icon={<CheckCircle2 className="w-4 h-4 text-emerald-400" />} badge="Verified">
            <pre className="text-xs bg-[#0D1522] rounded-xl p-3 overflow-x-auto border border-[#1E293B] text-[#82B1FF]">
              {JSON.stringify(auditData.real_chain, null, 2)}
            </pre>
          </CollapsibleSection>
        )}

        {auditData.fake_chain && (
          <CollapsibleSection title="Rejected Hallucinated Chain" icon={<XCircle className="w-4 h-4 text-rose-400" />} badge="Rejected">
            <pre className="text-xs bg-[#0D1522] rounded-xl p-3 overflow-x-auto border border-[#1E293B] text-rose-300/70">
              {JSON.stringify(auditData.fake_chain, null, 2)}
            </pre>
          </CollapsibleSection>
        )}

        {auditData.judge_reasoning && (
          <CollapsibleSection title="Judge Reasoning" icon={<Shield className="w-4 h-4 text-[#82B1FF]" />}>
            <p className="text-sm text-[#E2E8F0] leading-relaxed">{auditData.judge_reasoning}</p>
          </CollapsibleSection>
        )}

        {(auditData.duplicate_sources.length > 0 || auditData.pii_report.length > 0) && (
          <CollapsibleSection title="Data Quality" icon={<ShieldAlert className="w-4 h-4 text-amber-400" />}>
            {auditData.duplicate_sources.length > 0 && (
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                <span className="text-xs">Duplicates: {auditData.duplicate_sources.join(", ")}</span>
              </div>
            )}
            {auditData.pii_report.length > 0 && (
              <div className="flex items-start gap-2">
                <Shield className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span className="text-xs">PII entities redacted: {auditData.pii_report.length}</span>
              </div>
            )}
          </CollapsibleSection>
        )}
      </div>

      {/* Reference Detail Modal (Portal) */}
      {mounted && activeRef !== null && uniqueRefs[activeRef] && createPortal(
        <div className="fixed inset-0 z-[100] bg-[#090E17]/80 backdrop-blur-sm flex items-center justify-center p-4 md:p-8 animate-in fade-in duration-200">
          <div className="bg-[#0D1522] rounded-3xl p-6 md:p-8 shadow-2xl border border-[#222E40] w-full max-w-3xl max-h-[80vh] flex flex-col animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-[#132A4B] text-[#82B1FF] rounded-xl">
                  {getIcon(uniqueRefs[activeRef].source_type || guessType(uniqueRefs[activeRef].source))}
                </div>
                <div>
                  <h4 className="text-lg font-semibold text-white">{uniqueRefs[activeRef].source}</h4>
                  <p className="text-xs text-[#64748B]">Location: {uniqueRefs[activeRef].location}</p>
                </div>
              </div>
              <button onClick={() => setActiveRef(null)} className="p-2 text-[#94A3B8] hover:text-white rounded-xl hover:bg-[#151D2C] transition-colors">
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="flex-1 bg-[#090E17] rounded-2xl border border-[#222E40] p-6 overflow-auto">
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">Source Type:</span>
                  <span className="text-sm text-[#E2E8F0] font-medium">{uniqueRefs[activeRef].source_type || guessType(uniqueRefs[activeRef].source)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">Language:</span>
                  <span className="text-sm text-[#E2E8F0] font-medium">{uniqueRefs[activeRef].language || "en"}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">Location:</span>
                  <span className="text-sm text-[#E2E8F0] font-medium">{uniqueRefs[activeRef].location}</span>
                </div>
                <div className="mt-4 pt-4 border-t border-[#222E40]">
                  <p className="text-sm text-[#94A3B8]">This source was retrieved and used as grounding evidence by the self-auditing pipeline. The evidence chain in the Audit Trail shows exactly how this source contributed to the final answer.</p>
                </div>
              </div>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
}
