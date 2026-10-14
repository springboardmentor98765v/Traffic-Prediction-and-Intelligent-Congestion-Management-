import React from "react";

interface BadgeProps {
  variant?: "low" | "medium" | "high" | "critical" | "warning" | "advisory" | "admin" | "operator" | "public" | string;
  children: React.ReactNode;
  pulse?: boolean;
  className?: string;
}

export default function Badge({ variant = "low", children, pulse = false, className = "" }: BadgeProps) {
  const v = variant.toLowerCase();

  let colorClasses = "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
  let pulseDotColor = "bg-emerald-400";

  if (v === "medium" || v === "warning" || v === "moderate") {
    colorClasses = "bg-amber-500/15 text-amber-300 border-amber-500/30";
    pulseDotColor = "bg-amber-400";
  } else if (v === "high" || v === "critical" || v === "severe") {
    colorClasses = "bg-rose-500/15 text-rose-300 border-rose-500/30";
    pulseDotColor = "bg-rose-400";
  } else if (v === "admin") {
    colorClasses = "bg-purple-500/15 text-purple-300 border-purple-500/30";
    pulseDotColor = "bg-purple-400";
  } else if (v === "operator") {
    colorClasses = "bg-cyan-500/15 text-cyan-300 border-cyan-500/30";
    pulseDotColor = "bg-cyan-400";
  } else if (v === "advisory" || v === "public") {
    colorClasses = "bg-blue-500/15 text-blue-300 border-blue-500/30";
    pulseDotColor = "bg-blue-400";
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider border ${colorClasses} ${className}`}
    >
      {pulse && (
        <span className="relative flex h-2 w-2">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${pulseDotColor} opacity-75`}></span>
          <span className={`relative inline-flex rounded-full h-2 w-2 ${pulseDotColor}`}></span>
        </span>
      )}
      {children}
    </span>
  );
}
