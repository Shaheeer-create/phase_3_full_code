import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

export const metadata: Metadata = {
  title: "TodoAI - AI-Powered Task Management",
  description: "Next-generation task management with intelligent AI assistance",
  keywords: ["todo", "ai", "task management", "productivity", "chatbot"],
  authors: [{ name: "TodoAI" }],
  openGraph: {
    title: "TodoAI - AI-Powered Task Management",
    description: "Next-generation task management with intelligent AI assistance",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <ThemeProvider defaultTheme="dark" storageKey="todoai-theme">
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
