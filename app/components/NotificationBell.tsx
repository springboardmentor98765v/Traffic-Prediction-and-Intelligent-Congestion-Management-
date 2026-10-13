
"use client";

import { useCallback, useEffect, useState } from "react";
import { apiGet, apiPost } from "../../lib/api";

type AlertItem = {
  id: string | number;
  title?: string;
  message?: string;
  type?: string;
  is_read?: boolean;
  read?: boolean;
};

export default function NotificationBell() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const loadAlerts = useCallback(async () => {
    setLoading(true);

    try {
      const data = await apiGet<AlertItem[]>("/api/v1/alerts/my");
      setAlerts(Array.isArray(data) ? data : []);
      setError("");
    } catch {
      setError("Unable to load alerts. Check backend connection.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadAlerts();
    }, 0);

    const interval = window.setInterval(() => {
      void loadAlerts();
    }, 30000);

    return () => {
      window.clearTimeout(timer);
      window.clearInterval(interval);
    };
  }, [loadAlerts]);

  async function markRead(alert: AlertItem) {
    try {
      await apiPost(
        `/api/v1/alerts/${encodeURIComponent(String(alert.id))}/read`
      );

      setAlerts((items) =>
        items.map((item) =>
          item.id === alert.id
            ? { ...item, is_read: true, read: true }
            : item
        )
      );
      setError("");
    } catch {
      setError("Unable to mark alert as read.");
    }
  }

  const unread = alerts.filter(
    (alert) => !(alert.is_read ?? alert.read ?? false)
  ).length;

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        className="rounded-lg border px-3 py-2 text-sm"
      >
        🔔 Alerts {unread > 0 && `(${unread})`}
      </button>

      {open && (
        <div className="absolute right-0 z-50 mt-2 w-80 max-w-[90vw] rounded-xl border bg-white p-4 text-black shadow-xl">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-semibold">Traffic Alerts</h2>
            <button
              type="button"
              onClick={() => void loadAlerts()}
              disabled={loading}
              className="text-sm text-blue-700 underline"
            >
              {loading ? "Loading..." : "Refresh"}
            </button>
          </div>

          {error && (
            <p role="alert" className="mb-3 text-sm text-red-600">
              {error}
            </p>
          )}

          {!error && alerts.length === 0 && (
            <p className="text-sm text-gray-600">
              {loading ? "Loading alerts..." : "No notifications available."}
            </p>
          )}

          <div className="max-h-80 space-y-3 overflow-y-auto">
            {alerts.map((alert) => {
              const isRead = alert.is_read ?? alert.read ?? false;

              return (
                <div key={alert.id} className="rounded-lg border p-3">
                  <p className="font-medium">
                    {alert.title || alert.type || "Traffic alert"}
                  </p>
                  <p className="mt-1 text-sm text-gray-700">
                    {alert.message || "No details available."}
                  </p>

                  {!isRead && (
                    <button
                      type="button"
                      onClick={() => void markRead(alert)}
                      className="mt-2 text-sm text-blue-700 underline"
                    >
                      Mark as read
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
