import React from "react";

interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export default function ErrorMessage({
  title = "Connection Notice",
  message,
  onRetry,
  onDismiss,
}: ErrorMessageProps) {
  return (
    <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-200 backdrop-blur-md transition-all animate-fadeIn">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <span className="text-xl">⚠️</span>
          <div>
            <h4 className="font-semibold text-rose-300 text-sm">{title}</h4>
            <p className="mt-1 text-xs text-rose-200/90 leading-relaxed">{message}</p>
            {onRetry && (
              <button
                onClick={onRetry}
                className="mt-2.5 inline-flex items-center gap-1.5 rounded-lg bg-rose-600/30 hover:bg-rose-600/50 border border-rose-500/40 px-3 py-1 text-xs font-semibold text-rose-100 transition shadow-sm"
              >
                <span>🔄</span> Retry Request
              </button>
            )}
          </div>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-rose-400 hover:text-rose-200 text-lg leading-none"
            aria-label="Dismiss error"
          >
            &times;
          </button>
        )}
      </div>
    </div>
  );
}
