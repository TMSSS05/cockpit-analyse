import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { BarChart3 } from "lucide-react";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Cockpit d'Analyse Trading",
  description: "Dashboard d'analyse multi-actifs avec indicateurs techniques",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="fr"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-black text-zinc-100">
        <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-sm">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 py-3">
            <Link href="/" className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-emerald-400" />
              <span className="text-sm font-semibold text-zinc-100">
                Cockpit
              </span>
            </Link>
            <nav className="flex items-center gap-4">
              <Link
                href="/"
                className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
              >
                Dashboard
              </Link>
              <span className="text-xs text-zinc-700">|</span>
              <span className="text-xs text-zinc-600">v0.1.0</span>
            </nav>
          </div>
        </header>
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 sm:px-6 py-6">
          {children}
        </main>
      </body>
    </html>
  );
}
