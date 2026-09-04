import Link from "next/link";

export default function Sidebar() {
  return (
    <aside className="w-full md:w-64 min-h-auto md:min-h-screen bg-white border-r border-gray-200 p-4 md:p-6">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-800">
          Traffic Control
        </h2>

        <p className="text-sm text-gray-500 mt-1">
          Management Panel
        </p>
      </div>

      <nav className="space-y-2">
        <Link
          href="/dashboard"
          className="block rounded-lg px-4 py-3 text-gray-700 hover:bg-blue-100 hover:text-blue-700 transition"
        >
          📊 Dashboard
        </Link>

        <Link
          href="/live-map"
          className="block rounded-lg px-4 py-3 text-gray-700 hover:bg-blue-100 hover:text-blue-700 transition"
        >
          🗺️ Live Traffic Map
        </Link>

        <Link
          href="/alerts"
          className="block rounded-lg px-4 py-3 text-gray-700 hover:bg-blue-100 hover:text-blue-700 transition"
        >
          🚨 Traffic Alerts
        </Link>

        <Link
         href="/analytics"
          className="block rounded-lg px-4 py-3 text-gray-700 hover:bg-blue-100 hover:text-blue-700 transition"
          >
           📈 Analytics
          </Link>

        <Link
          href="/login"
          className="block rounded-lg px-4 py-3 text-gray-700 hover:bg-blue-100 hover:text-blue-700 transition"
        >
          🔐 Login
        </Link>

        <Link
          href="/register"
          className="block rounded-lg px-4 py-3 text-gray-700 hover:bg-blue-100 hover:text-blue-700 transition"
        >
          📝 Register
        </Link>
      </nav>
    </aside>
  );
}