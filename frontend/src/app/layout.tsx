import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-provider";
import { FloatingChatButton } from "@/components/chat";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Todo Evolution - Organize Your Tasks",
  description: "A modern todo application with recurring tasks and due dates",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* ChatKit Script for OpenAI ChatKit integration */}
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="beforeInteractive"
        />
      </head>
      <body
        className={`${inter.className} antialiased`}
        suppressHydrationWarning
      >
        <AuthProvider>
          {children}
          {/* Global floating chat button */}
          <FloatingChatButton />
        </AuthProvider>
      </body>
    </html>
  );
}
