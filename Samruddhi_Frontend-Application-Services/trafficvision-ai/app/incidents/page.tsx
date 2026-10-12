'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { Sidebar } from '@/components/Sidebar';

const API = 'http://127.0.0.1:8002/api/v1';

type Severity = 'High' | 'Medium' | 'Low';

interface Road {
  id: string;
  name: string;
}

interface AlertItem {
  alert_id: number;
  type: string;
  severity: string;
  road_id: number;
  message: string;
  read?: boolean;
  created_at?: string;
}

interface Incident {
  id: number;
  type: string;
  severity: Severity;
  roadId: number;
  roadName: string;
  message: string;
  read: boolean;
  createdAt?: string;
}

function normalizeSeverity(value: string): Severity {
  const valueLower = value.toLowerCase();
  if (valueLower === 'high' || valueLower === 'critical') return 'High';
  if (valueLower === 'low') return 'Low';
  return 'Medium';
}

function severityClass(severity: Severity) {
  if (severity === 'High') return 'border-red-500/30 bg-red-500/10 text-red-400';
  if (severity === 'Medium') return 'border-amber-500/30 bg-amber-500/10 text-amber-400';
  return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400';
}

export default function IncidentsPage() {
  const [role, setRole] = useState('Operator');

  useEffect(() => {
    const savedRole = localStorage.getItem('userRole');
    if (savedRole) setRole(savedRole);
  }, []);
  const [roads, setRoads] = useState<Road[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [roadId, setRoadId] = useState('');
  const [incidentType, setIncidentType] = useState('Accident');
  const [severity, setSeverity] = useState<Severity>('High');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [readingId, setReadingId] = useState<number | null>(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const headers = useCallback((): HeadersInit => {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }, []);

  const fetchAlerts = useCallback(async (roadList: Road[]) => {
    const requestHeaders = headers();
    let response = await fetch(`${API}/alerts/active`, {
      headers: requestHeaders,
      cache: 'no-store',
    });

    if (response.status === 401 || response.status === 403) {
      response = await fetch(`${API}/alerts/my`, {
        headers: requestHeaders,
        cache: 'no-store',
      });
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(
        typeof data.detail === 'string'
          ? data.detail
          : `Alert request failed (${response.status}).`
      );
    }

    const list: AlertItem[] = Array.isArray(data) ? data : [];

    const myResponse = await fetch(`${API}/alerts/my`, {
      headers: requestHeaders,
      cache: 'no-store',
    });

    const myData = myResponse.ok
      ? await myResponse.json().catch(() => [])
      : [];

    const readStatus = new Map<number, boolean>(
      (Array.isArray(myData) ? myData : []).map(
        (item: { alert_id: number; read: boolean }) =>
          [item.alert_id, Boolean(item.read)] as [number, boolean]
      )
    );

    setIncidents(
      list.map((item) => ({
        id: item.alert_id,
        type: item.type || 'Traffic Incident',
        severity: normalizeSeverity(item.severity || 'Medium'),
        roadId: item.road_id,
        roadName:
          roadList.find((road) => Number(road.id) === item.road_id)?.name ||
          `Road #${item.road_id}`,
        message: item.message || 'No description provided.',
        read: readStatus.has(item.alert_id) ? readStatus.get(item.alert_id)! : Boolean(item.read),
        createdAt: item.created_at,
      }))
    );
  }, [headers]);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API}/traffic/nodes`, {
        cache: 'no-store',
      });
      const data = await response.json().catch(() => []);

      if (!response.ok) {
        throw new Error(`Road request failed (${response.status}).`);
      }

      const list: Road[] = (Array.isArray(data) ? data : []).map(
        (item: { id: string | number; name: string }) => ({
          id: String(item.id),
          name: item.name,
        })
      );

      setRoads(list);
      setRoadId((current) => current || list[0]?.id || '');
      await fetchAlerts(list);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Unable to load backend data.'
      );
    } finally {
      setLoading(false);
    }
  }, [fetchAlerts]);

  useEffect(() => {
    setRole(localStorage.getItem('userRole') || 'Operator');
    refresh();
  }, [refresh]);

  async function reportIncident(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setNotice('');

    if (!roadId) {
      setError('No roads are available. Check the backend traffic nodes.');
      return;
    }

    if (!message.trim()) {
      setError('Please enter an incident description.');
      return;
    }

    setSubmitting(true);

    try {
      const response = await fetch(`${API}/alerts`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({
          type: incidentType,
          severity,
          road_id: Number(roadId),
          message: message.trim(),
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : `Incident submission failed (${response.status}).`
        );
      }

      setMessage('');
      setNotice(`Incident submitted successfully. Alert ID: ${data.alert_id ?? 'created'}.`);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not submit incident.');
    } finally {
      setSubmitting(false);
    }
  }

  async function markRead(id: number) {
    setError('');
    setNotice('');
    setReadingId(id);

    try {
      const response = await fetch(`${API}/alerts/${id}/read`, {
        method: 'POST',
        headers: headers(),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : `Could not mark alert as read (${response.status}).`
        );
      }

      setIncidents((current) =>
        current.map((item) => item.id === id ? { ...item, read: true } : item)
      );
      setNotice(`Alert #${id} marked as read.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not update alert.');
    } finally {
      setReadingId(null);
    }
  }

  const unreadCount = incidents.filter((item) => !item.read).length;

  return (
    <div className="flex min-h-screen bg-[#1c1d28] text-white">
      <Sidebar role={role} />

      <main className="min-w-0 flex-1 overflow-y-auto p-5 md:p-8">
        <div className="mx-auto max-w-6xl space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 className="text-2xl font-bold">Incident &amp; System Alerts Panel</h1>
              <p className="mt-1 text-sm text-gray-400">
                Report traffic events and manage control center alerts in real time.
              </p>
            </div>
            <button
              type="button"
              onClick={refresh}
              disabled={loading}
              className="rounded-xl border border-white/10 bg-[#25283c] px-4 py-2 text-sm hover:border-purple-400 disabled:opacity-50"
            >
              {loading ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>

          {error && (
            <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
              {error}
            </div>
          )}
          {notice && (
            <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-300">
              {notice}
            </div>
          )}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-white/5 bg-[#25283c] p-5">
              <p className="text-sm text-gray-400">Alerts from backend</p>
              <p className="mt-2 text-3xl font-bold">{incidents.length}</p>
            </div>
            <div className="rounded-2xl border border-white/5 bg-[#25283c] p-5">
              <p className="text-sm text-gray-400">Unread alerts</p>
              <p className="mt-2 text-3xl font-bold text-amber-400">{unreadCount}</p>
            </div>
            <div className="rounded-2xl border border-white/5 bg-[#25283c] p-5">
              <p className="text-sm text-gray-400">Available road nodes</p>
              <p className="mt-2 text-3xl font-bold text-purple-400">{roads.length}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <section className="rounded-2xl border border-white/5 bg-[#25283c] p-6">
              <h2 className="text-lg font-bold">Log New Incident</h2>
              <p className="mt-1 text-xs text-gray-400">
                Signed in as {role}
              </p>

              <form onSubmit={reportIncident} className="mt-5 space-y-4">
                <div>
                  <label className="mb-2 block text-sm text-gray-300">Road / Node Name</label>
                  <select
                    value={roadId}
                    onChange={(event) => setRoadId(event.target.value)}
                    required
                    disabled={!roads.length}
                    className="w-full rounded-xl border border-white/10 bg-[#1c1d28] p-3 text-sm outline-none focus:border-purple-500"
                  >
                    <option value="">Select road</option>
                    {roads.map((road) => (
                      <option key={road.id} value={road.id}>{road.name}</option>
                    ))}
                  </select>
                  {!roads.length && (
                    <p className="mt-1 text-xs text-amber-300">
                      No road nodes returned by the backend.
                    </p>
                  )}
                </div>

                <div>
                  <label className="mb-2 block text-sm text-gray-300">Incident Type</label>
                  <select
                    value={incidentType}
                    onChange={(event) => setIncidentType(event.target.value)}
                    className="w-full rounded-xl border border-white/10 bg-[#1c1d28] p-3 text-sm outline-none focus:border-purple-500"
                  >
                    <option>Accident</option>
                    <option>Road Work</option>
                    <option>Heavy Congestion</option>
                    <option>Signal Failure</option>
                    <option>Road Closure</option>
                    <option>Vehicle Breakdown</option>
                    <option>Other</option>
                  </select>
                </div>

                <div>
                  <label className="mb-2 block text-sm text-gray-300">Severity Level</label>
                  <select
                    value={severity}
                    onChange={(event) => setSeverity(event.target.value as Severity)}
                    className="w-full rounded-xl border border-white/10 bg-[#1c1d28] p-3 text-sm outline-none focus:border-purple-500"
                  >
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>

                <div>
                  <label className="mb-2 block text-sm text-gray-300">Description</label>
                  <textarea
                    value={message}
                    onChange={(event) => setMessage(event.target.value)}
                    required
                    maxLength={1000}
                    rows={4}
                    placeholder="Describe the incident..."
                    className="w-full rounded-xl border border-white/10 bg-[#1c1d28] p-3 text-sm outline-none placeholder:text-gray-500 focus:border-purple-500"
                  />
                </div>

                <button
                  type="submit"
                  disabled={submitting || !roads.length}
                  className="w-full rounded-xl bg-purple-600 px-4 py-3 text-sm font-semibold hover:bg-purple-500 disabled:opacity-50"
                >
                  {submitting ? 'Submitting...' : 'Report Incident'}
                </button>
              </form>
            </section>

            <section className="rounded-2xl border border-white/5 bg-[#25283c] p-6 lg:col-span-2">
              <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-lg font-bold">Active System Incidents</h2>
                  <p className="mt-1 text-xs text-gray-400">
                    Alert records returned by the backend API
                  </p>
                </div>
                <span className="rounded-full border border-purple-500/30 bg-purple-500/10 px-3 py-1 text-xs text-purple-300">
                  {incidents.length} alert(s)
                </span>
              </div>

              {loading ? (
                <p className="py-10 text-center text-sm text-gray-400">Loading alerts...</p>
              ) : incidents.length === 0 ? (
                <div className="rounded-xl border border-dashed border-white/10 py-12 text-center">
                  <p className="font-medium">No alerts returned</p>
                  <p className="mt-2 text-xs text-gray-400">
                    Submit an incident or refresh to check again.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {incidents.map((item) => (
                    <article
                      key={item.id}
                      className="rounded-xl border border-white/10 bg-[#1c1d28] p-4"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div className="flex flex-wrap items-center gap-2">
                            <h3 className="font-semibold">{item.roadName}</h3>
                            <span className={`rounded-full border px-2 py-1 text-[10px] font-bold uppercase ${severityClass(item.severity)}`}>
                              {item.severity}
                            </span>
                            {item.read && (
                              <span className="text-[10px] text-gray-500">READ</span>
                            )}
                          </div>
                          <p className="mt-2 text-sm text-gray-300">
                            Type: {item.type}
                          </p>
                          <p className="mt-1 break-words text-sm text-gray-400">
                            {item.message}
                          </p>
                          <p className="mt-2 text-xs text-gray-500">
                            Alert #{item.id}
                            {item.createdAt
                              ? ` · ${new Date(item.createdAt).toLocaleString()}`
                              : ''}
                          </p>
                        </div>

                        {!item.read && (
                          <button
                            type="button"
                            onClick={() => markRead(item.id)}
                            disabled={readingId === item.id}
                            className="shrink-0 rounded-lg border border-white/10 px-3 py-2 text-xs hover:border-purple-400 disabled:opacity-50"
                          >
                            {readingId === item.id ? 'Updating...' : 'Mark as read'}
                          </button>
                        )}
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}
