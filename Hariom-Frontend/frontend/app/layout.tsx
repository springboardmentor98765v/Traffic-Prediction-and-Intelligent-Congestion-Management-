import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "./lib/auth-context";
import { TrafficProvider } from "./lib/traffic-context";

export const metadata: Metadata = {
  title: "TrafficVision AI — Intelligent Congestion Management & Prediction",
  description: "AI-driven smart traffic monitoring, congestion forecasting, and route optimization platform.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090d16] text-slate-100 antialiased">
        <AuthProvider>
          <TrafficProvider>
            {children}
          </TrafficProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
