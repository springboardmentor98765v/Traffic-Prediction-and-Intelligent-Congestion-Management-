import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="flex items-center justify-between bg-blue-700 px-8 py-4 text-white shadow">
      <Link href="/dashboard" className="text-xl font-bold">
        TrafficVision AI
      </Link>

      <div className="flex gap-6">
        <Link href="/dashboard" className="hover:text-blue-200">
          Dashboard
        </Link>

        <Link href="/live-map" className="hover:text-blue-200">
          Live Map
        </Link>

        <Link href="/alerts" className="hover:text-blue-200">
          Alerts
        </Link>

        <Link href="/login" className="hover:text-blue-200">
          Login
        </Link>

        <Link href="/register" className="hover:text-blue-200">
          Register
        </Link>
      </div>
    </nav>
  );
}