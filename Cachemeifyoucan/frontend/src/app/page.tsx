"use client";

import { signIn, useSession } from "next-auth/react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, User, ArrowRight, Loader2 } from "lucide-react";

function GoogleIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      />
    </svg>
  );
}

function GitHubIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
    </svg>
  );
}

type LoadingState = "google" | "github" | "guest" | null;

export default function LoginPage() {
  const [loading, setLoading] = useState<LoadingState>(null);
  const { status } = useSession();
  const router = useRouter();

  // If already authenticated and not just signed out, go to dashboard
  useEffect(() => {
    if (status === "authenticated" && !window.location.search.includes("signedOut")) {
      router.replace("/dashboard");
    }
  }, [status, router]);

  const handleSignIn = async (provider: "google" | "github") => {
    setLoading(provider);
    try {
      await signIn(provider, { callbackUrl: "/dashboard" });
    } catch {
      setLoading(null);
    }
  };

  const handleGuestSignIn = async () => {
    setLoading("guest");
    try {
      await signIn("guest", {
        name: "Guest User",
        callbackUrl: "/dashboard",
      });
    } catch {
      setLoading(null);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#090E17] relative overflow-hidden font-sans">
      {/* ── Animated mesh background ── */}
      <div
        className="absolute top-[10%] left-[15%] w-[500px] h-[500px] bg-[#132A4B]/50 rounded-full filter blur-[130px] animate-blob"
        style={{ animationDelay: "0s" }}
      />
      <div
        className="absolute bottom-[10%] right-[10%] w-[450px] h-[450px] bg-[#1a3a6e]/35 rounded-full filter blur-[130px] animate-blob"
        style={{ animationDelay: "3s" }}
      />
      <div
        className="absolute top-[50%] left-[55%] w-[300px] h-[300px] bg-[#0f2040]/40 rounded-full filter blur-[100px] animate-blob"
        style={{ animationDelay: "6s" }}
      />

      {/* ── Subtle grid overlay ── */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(#82B1FF 1px, transparent 1px), linear-gradient(90deg, #82B1FF 1px, transparent 1px)",
          backgroundSize: "48px 48px",
        }}
      />

      {/* ── Main card ── */}
      <div className="z-10 glass-card rounded-[2rem] w-full max-w-[440px] p-10 sm:p-12 flex flex-col items-center animate-fade-up">

        {/* Brand */}
        <div className="flex items-center gap-3 mb-10 group cursor-default">
          <div className="relative">
            <div className="p-3 bg-[#132A4B] text-[#82B1FF] rounded-2xl shadow-[0_4px_20px_rgba(130,177,255,0.2)] group-hover:shadow-[0_4px_28px_rgba(130,177,255,0.35)] transition-shadow duration-300 animate-pulse-ring">
              <Sparkles className="w-7 h-7" />
            </div>
          </div>
          <div>
            <h1 className="text-[28px] font-bold text-white tracking-tight leading-none">
              VeriSync<span className="text-[#64748B] font-light">_ai</span>
            </h1>
            <p className="text-[11px] text-[#4A5A6E] uppercase tracking-[0.15em] font-medium mt-0.5">
              Self-Auditing RAG
            </p>
          </div>
        </div>

        {/* Heading */}
        <h2 className="text-[22px] font-semibold text-[#E2E8F0] mb-2 text-center">
          Welcome back
        </h2>
        <p className="text-[14px] leading-relaxed text-[#64748B] mb-8 text-center max-w-[270px]">
          Sign in to access your provably-grounded intelligence assistant.
        </p>

        {/* Divider */}
        <div className="w-full flex items-center gap-3 mb-6">
          <div className="flex-1 h-px bg-[#222E40]" />
          <span className="text-[11px] text-[#3D4F65] uppercase tracking-wider font-medium">
            Continue with
          </span>
          <div className="flex-1 h-px bg-[#222E40]" />
        </div>

        {/* Auth Buttons */}
        <div className="w-full flex flex-col gap-3">
          {/* Google */}
          <button
            id="btn-google-signin"
            onClick={() => handleSignIn("google")}
            disabled={!!loading}
            className="auth-btn auth-btn-primary glow-border disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading === "google" ? (
              <Loader2 className="w-5 h-5 animate-spin text-[#82B1FF]" />
            ) : (
              <GoogleIcon />
            )}
            <span>Continue with Google</span>
          </button>

          {/* GitHub */}
          <button
            id="btn-github-signin"
            onClick={() => handleSignIn("github")}
            disabled={!!loading}
            className="auth-btn auth-btn-primary glow-border disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading === "github" ? (
              <Loader2 className="w-5 h-5 animate-spin text-[#82B1FF]" />
            ) : (
              <GitHubIcon />
            )}
            <span>Continue with GitHub</span>
          </button>

          {/* Divider */}
          <div className="flex items-center gap-3 my-1">
            <div className="flex-1 h-px bg-[#1A2435]" />
            <span className="text-[11px] text-[#3D4F65]">or</span>
            <div className="flex-1 h-px bg-[#1A2435]" />
          </div>

          {/* Guest */}
          <button
            id="btn-guest-signin"
            onClick={handleGuestSignIn}
            disabled={!!loading}
            className="auth-btn border border-dashed border-[#2A3A52] bg-transparent text-[#64748B] hover:text-[#94A3B8] hover:border-[#33588D] hover:bg-[#0f1e30]/50 transition-all duration-200 group disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading === "guest" ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <User className="w-5 h-5" />
            )}
            <span>Continue as Guest</span>
            {loading !== "guest" && (
              <ArrowRight className="w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
            )}
          </button>
        </div>

        {/* Feature badges */}
        <div className="mt-8 flex flex-wrap justify-center gap-2">
          {["Adversarial Auditing", "PII Redaction", "Multi-Modal RAG"].map((f) => (
            <span
              key={f}
              className="text-[10px] text-[#4A5A6E] bg-[#0F1A27] border border-[#1A2840] px-2.5 py-1 rounded-full font-medium"
            >
              {f}
            </span>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-[12px] leading-relaxed text-[#3D4F65] max-w-[280px]">
          By continuing, you agree to VeriSync_ai&apos;s{" "}
          <a href="#" className="hover:text-[#82B1FF] transition-colors underline underline-offset-2 decoration-[#1A2840]">
            Terms of Service
          </a>{" "}
          and{" "}
          <a href="#" className="hover:text-[#82B1FF] transition-colors underline underline-offset-2 decoration-[#1A2840]">
            Privacy Policy
          </a>
          .
        </div>
      </div>
    </div>
  );
}
