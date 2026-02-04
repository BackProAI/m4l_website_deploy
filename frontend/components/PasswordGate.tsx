'use client';

import { FormEvent, PropsWithChildren, useCallback, useEffect, useRef, useState } from "react";
import { Eye, EyeOff } from "lucide-react";

const PASSWORD = "Georgia1";
const STORAGE_KEY = "m4l_site_access_window";
const ACCESS_WINDOW_MS = 8 * 60 * 60 * 1000; // 8 hours
const MAX_DRIFT_MS = 1000; // tolerate small timing differences

type GateStatus = "checking" | "prompt" | "granted";

export default function PasswordGate({ children }: PropsWithChildren<object>) {
  const [status, setStatus] = useState<GateStatus>("checking");
  const [expiresAt, setExpiresAt] = useState<number | null>(null);
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearGateTimer = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  const lockSite = useCallback(() => {
    clearGateTimer();
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (err) {
      console.warn("Unable to clear stored access window", err);
    }
    setStatus("prompt");
    setExpiresAt(null);
    setInput("");
    setError("");
  }, [clearGateTimer]);

  const isExpiryValid = useCallback((expiry: number) => {
    if (typeof expiry !== "number") {
      return false;
    }
    const now = Date.now();
    if (expiry <= now) {
      return false;
    }
    return expiry - now <= ACCESS_WINDOW_MS + MAX_DRIFT_MS;
  }, []);

  const readStoredAccess = useCallback(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        return false;
      }
      const parsed = JSON.parse(raw);
      const storedExpiry = typeof parsed?.expiresAt === "number" ? parsed.expiresAt : Number(parsed);
      if (isExpiryValid(storedExpiry)) {
        setExpiresAt(storedExpiry);
        setStatus("granted");
        return true;
      }
    } catch (err) {
      console.warn("Unable to read stored access window", err);
    }
    lockSite();
    return false;
  }, [isExpiryValid, lockSite]);

  useEffect(() => {
    if (!readStoredAccess()) {
      setStatus("prompt");
    }
  }, [readStoredAccess]);

  useEffect(() => {
    clearGateTimer();
    if (status !== "granted" || !expiresAt) {
      return;
    }
    const msRemaining = expiresAt - Date.now();
    if (msRemaining <= 0) {
      lockSite();
      return;
    }
    timeoutRef.current = setTimeout(lockSite, msRemaining);
    return clearGateTimer;
  }, [status, expiresAt, lockSite, clearGateTimer]);

  useEffect(() => {
    const handleStorage = (event: StorageEvent) => {
      if (event.key !== STORAGE_KEY) {
        return;
      }
      if (!event.newValue) {
        lockSite();
        return;
      }
      try {
        const parsed = JSON.parse(event.newValue);
        const newExpiry = typeof parsed?.expiresAt === "number" ? parsed.expiresAt : null;
        if (newExpiry && isExpiryValid(newExpiry)) {
          setExpiresAt(newExpiry);
          setStatus("granted");
        } else {
          lockSite();
        }
      } catch (err) {
        console.warn("Unable to sync stored access window", err);
        lockSite();
      }
    };
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, [isExpiryValid, lockSite]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    if (input.trim() !== PASSWORD) {
      setError("Incorrect password. Please try again.");
      return;
    }

    const expiry = Date.now() + ACCESS_WINDOW_MS;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ expiresAt: expiry }));
    } catch (err) {
      console.warn("Unable to persist access window", err);
    }

    setExpiresAt(expiry);
    setStatus("granted");
    setInput("");
  };

  if (status === "granted") {
    return <>{children}</>;
  }

  if (status === "checking") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white">
        <p className="text-sm text-slate-300">Preparing workspace...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/70 p-8 shadow-2xl">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-semibold">Restricted Area</h1>
          <p className="mt-2 text-sm text-slate-300">
            Enter the shared password to access the dashboard. Access lasts for 8 hours.
          </p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <label htmlFor="site-password" className="text-sm font-medium text-slate-200">
              Password
            </label>
            <div className="relative">
              <input
                id="site-password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                className="w-full rounded-xl border border-slate-600 bg-slate-900/40 px-4 py-3 pr-12 text-base text-slate-50 placeholder-slate-500 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400"
                placeholder="Enter password"
                aria-invalid={error ? "true" : "false"}
                aria-describedby={error ? "site-password-error" : undefined}
              />
              <button
                type="button"
                onClick={() => setShowPassword((prev) => !prev)}
                className="absolute inset-y-0 right-3 flex items-center text-slate-400 hover:text-slate-100"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} aria-hidden /> : <Eye size={18} aria-hidden />}
              </button>
            </div>
            {error && (
              <p id="site-password-error" className="text-sm text-rose-400">
                {error}
              </p>
            )}
          </div>
          <button
            type="submit"
            className="w-full rounded-xl bg-cyan-500 px-4 py-3 font-semibold text-slate-950 transition hover:bg-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-300 focus:ring-offset-2 focus:ring-offset-slate-900"
          >
            Unlock Workspace
          </button>
        </form>
      </div>
    </div>
  );
}
