import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Nav from "@/components/Nav";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "PGxBD — Bangladeshi Pharmacogenomic Frequency Database",
  description:
    "Pharmacogenomic allele frequency database for the Bangladeshi (BEB) population, built from 1000 Genomes Project data.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <Nav />
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6">
          {children}
        </main>
        <footer className="border-t border-border">
          <div className="mx-auto max-w-6xl px-4 py-6 text-xs text-muted sm:px-6">
            PGxBD v2.0.0 — 1000 Genomes Project phase 3 (GRCh37), PharmGKB, CPIC. Research use
            only.
          </div>
        </footer>
      </body>
    </html>
  );
}
