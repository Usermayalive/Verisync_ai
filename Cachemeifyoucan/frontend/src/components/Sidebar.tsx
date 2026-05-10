"use client";

import { MessageSquare, LogOut, User, PlusCircle } from "lucide-react";
import { useSession, signOut } from "next-auth/react";
import Image from "next/image";

export default function Sidebar({ className = "", onNewChat }: { className?: string; onNewChat?: () => void }) {
  const { data: session } = useSession();

  const histories = [
    "Brainstorming App Ideas",
    "Tailwind CSS Tricks",
    "React Performance",
    "Next.js App Router Guide",
  ];

  const userName = session?.user?.name ?? "Guest User";
  const userEmail = session?.user?.email ?? "guest@verisync.ai";
  const userImage = session?.user?.image;
  const isGuest = !session?.user?.image;

  const handleSignOut = async () => {
    await signOut({ callbackUrl: "/?signedOut=1" });
  };

  return (
    <div
      className={`group flex flex-col h-full bg-[#0D1522] border-r border-[#222E40] transition-all duration-300 ease-in-out w-14 hover:w-[260px] overflow-hidden relative shrink-0 z-20 ${className}`}
    >
      {/* Collapsed View: Vertical Text + New Chat Icon */}
      <div className="absolute inset-0 flex flex-col items-center justify-start pt-6 opacity-100 group-hover:opacity-0 transition-opacity duration-200">
        <button 
          onClick={onNewChat}
          title="New Chat"
          className="mb-8 p-2 text-[#82B1FF] hover:bg-[#132A4B] rounded-lg transition-colors pointer-events-auto"
        >
          <PlusCircle className="w-5 h-5 pointer-events-auto" />
        </button>
        <span
          className="text-[11px] font-bold text-[#64748B] uppercase tracking-[0.3em] whitespace-nowrap pointer-events-none"
          style={{
            writingMode: "vertical-rl",
            textOrientation: "mixed",
            transform: "rotate(180deg)",
          }}
        >
          Chat History
        </span>
      </div>
      {/* Expanded View: Full Sidebar Contents */}
      <div className="w-[260px] flex flex-col h-full opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 delay-100">
        <div className="mb-4 px-4 pt-6 shrink-0">
          <button
            onClick={onNewChat}
            className="w-full flex items-center gap-3 px-3 py-2.5 text-sm font-semibold text-[#82B1FF] rounded-xl bg-[#132A4B]/40 hover:bg-[#132A4B] border border-[#222E40] hover:border-[#33588D] transition-all"
          >
            <PlusCircle className="w-5 h-5 shrink-0" />
            <span>New Chat</span>
          </button>
        </div>

        <div className="mb-2 px-4 shrink-0">
          <h2 className="text-sm font-semibold text-[#E2E8F0] uppercase tracking-wider">
            Chat Histories
          </h2>
        </div>

        <div className="flex-1 overflow-y-auto space-y-1 px-3">
          {histories.map((title, i) => (
            <button
              key={i}
              className="w-full flex items-center gap-3 px-3 py-2.5 text-[13px] text-[#94A3B8] hover:text-white rounded-xl hover:bg-[#151D2C] transition-colors text-left"
            >
              <MessageSquare className="w-4 h-4 shrink-0 text-[#64748B]" />
              <span className="truncate">{title}</span>
            </button>
          ))}
        </div>

        {/* User section */}
        <div className="mt-auto pt-4 border-t border-[#222E40] p-4 shrink-0">
          <div className="flex items-center gap-3 px-2 py-2 rounded-xl hover:bg-[#151D2C] cursor-pointer transition-colors group/user">
            {/* Avatar */}
            <div className="w-9 h-9 rounded-full bg-[#132A4B] flex items-center justify-center text-[#82B1FF] overflow-hidden shrink-0">
              {userImage ? (
                <Image
                  src={userImage}
                  alt={userName}
                  width={36}
                  height={36}
                  className="object-cover w-full h-full"
                />
              ) : (
                <User className="w-5 h-5" />
              )}
            </div>

            {/* Name + email */}
            <div className="flex-1 min-w-0 pr-2">
              <p className="text-sm font-medium text-white truncate">{userName}</p>
              <p className="text-xs text-[#94A3B8] truncate">
                {isGuest ? "Guest Session" : userEmail}
              </p>
            </div>

            {/* Sign Out */}
            <button
              onClick={handleSignOut}
              title="Sign out"
              className="p-1.5 opacity-0 group-hover/user:opacity-100 transition-opacity bg-[#151D2C] hover:bg-[#222E40] text-[#94A3B8] hover:text-white rounded-lg flex shrink-0 border border-[#222E40]"
            >
              <LogOut className="w-4 h-4 shadow-sm" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
