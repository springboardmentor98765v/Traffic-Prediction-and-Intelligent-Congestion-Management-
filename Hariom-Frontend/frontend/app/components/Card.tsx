import React from "react";

interface CardProps {
  title?: string;
  subtitle?: string;
  icon?: string;
  badge?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  headerAction?: React.ReactNode;
  glow?: boolean;
}

export default function Card({
  title,
  subtitle,
  icon,
  badge,
  children,
  className = "",
  headerAction,
  glow = false,
}: CardProps) {
  return (
    <div
      className={`rounded-2xl transition-all duration-300 ${
        glow ? "glass-panel-glow" : "glass-panel"
      } p-5 hover:border-slate-600/60 ${className}`}
    >
      {(title || icon || badge || headerAction) && (
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/80">
          <div className="flex items-center gap-2.5">
            {icon && <span className="text-xl">{icon}</span>}
            <div>
              {title && <h3 className="font-semibold text-slate-100 text-sm tracking-wide">{title}</h3>}
              {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {badge}
            {headerAction}
          </div>
        </div>
      )}
      <div>{children}</div>
    </div>
  );
}
