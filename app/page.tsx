import Link from "next/link";

export default function Home() {
  return (
    <main className="flex-1 bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <div className="max-w-5xl mx-auto px-6 py-16 text-center">
        <div className="inline-flex items-center gap-2 rounded-full bg-blue-100 px-4 py-1.5 text-xs font-bold text-blue-800 uppercase tracking-wide mb-6">
          <span>🚀</span>
          <span>Milestone 1 — System Core & Integration Increment</span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 tracking-tight leading-tight">
          TrafficVision AI
        </h1>
        <p className="mt-2 text-xl font-medium text-blue-700">
          Smart Traffic Prediction & Congestion Management System
        </p>

        <p className="mt-4 max-w-2xl mx-auto text-base text-gray-600">
          Centralized urban traffic platform integrating real-time telemetry ingestion,
          automated congestion scoring, role-based access control, and heuristic AI forecasting.
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <Link
            href="/dashboard"
            className="rounded-xl bg-blue-600 px-6 py-3 text-sm font-bold text-white shadow-lg hover:bg-blue-700 transition"
          >
            Launch Traffic Dashboard
          </Link>
          <Link
            href="/live-map"
            className="rounded-xl bg-white border border-gray-300 px-6 py-3 text-sm font-bold text-gray-700 shadow-sm hover:bg-gray-50 transition"
          >
            Explore Live Map
          </Link>
          <Link
            href="/login"
            className="rounded-xl bg-indigo-50 border border-indigo-200 px-6 py-3 text-sm font-bold text-indigo-700 hover:bg-indigo-100 transition"
          >
            Sign In (Admin / Operator)
          </Link>
        </div>

        {/* Feature Highlights Grid */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="rounded-2xl bg-white p-6 shadow-sm border border-gray-200">
            <div className="text-2xl mb-2">🔐</div>
            <h3 className="font-bold text-gray-900">JWT & RBAC Security</h3>
            <p className="text-xs text-gray-600 mt-1">
              Role-based access control for Admins, Operators, and Public Commuters with token refresh cycles.
            </p>
          </div>

          <div className="rounded-2xl bg-white p-6 shadow-sm border border-gray-200">
            <div className="text-2xl mb-2">📡</div>
            <h3 className="font-bold text-gray-900">Live Telemetry Pipeline</h3>
            <p className="text-xs text-gray-600 mt-1">
              Real-time ingestion for corridors R001–R005, density tracking, and resilient caching.
            </p>
          </div>

          <div className="rounded-2xl bg-white p-6 shadow-sm border border-gray-200">
            <div className="text-2xl mb-2">🤖</div>
            <h3 className="font-bold text-gray-900">Heuristic Prediction Stub</h3>
            <p className="text-xs text-gray-600 mt-1">
              Rule-based heuristic congestion forecast unblocking UI integration ahead of M2 ML model.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}