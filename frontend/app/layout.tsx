import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import ErrorBoundary from "@/components/ErrorBoundary";
import PasswordGate from "@/components/PasswordGate";
import BackendWarmup from "@/components/BackendWarmup";
import { Toaster } from 'react-hot-toast';

export const metadata: Metadata = {
  title: "More4Life - Automation Hub",
  description: "Streamline your workflow with AI-powered automation tools",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <script dangerouslySetInnerHTML={{ __html: `(() => {
          try {
            const theme = localStorage.getItem('theme');
            const root = document.documentElement;
            const body = document.body;
            const setDark = (d) => {
              if (d) { root.classList.add('dark'); body.classList.add('dark'); root.setAttribute('data-theme','dark'); }
              else { root.classList.remove('dark'); body.classList.remove('dark'); root.setAttribute('data-theme','light'); }
            };
            if (theme === 'dark' || theme === 'light') {
              setDark(theme === 'dark');
            } else {
              const m = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)');
              setDark(m && m.matches);
            }
          } catch (e) { /* ignore */ }
        })()` }} />
        <ErrorBoundary>
          <PasswordGate>
            <BackendWarmup />
            <div className="flex h-screen overflow-hidden">
              <Sidebar />
              {children}
            </div>
          </PasswordGate>
        </ErrorBoundary>
        <Toaster position="top-right" />
      </body>
    </html>
  );
}
