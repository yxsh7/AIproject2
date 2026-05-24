import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { cn } from '../lib/utils';
import { Providers } from '../components/providers';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "DevMetrics AI - Engineering Intelligence Platform",
  description: "AI-powered productivity analytics for engineering teams",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={cn(inter.className, "min-h-screen bg-background antialiased")}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
