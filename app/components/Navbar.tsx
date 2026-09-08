"use client";

import Link from "next/link";
import { useAuth } from "../lib/auth-context";

export default function Navbar() {
  const { user, role, isAuthenticated, logout } = useAuth();

  const getRoleBadgeColor = (r: string) => {
    switch (r.toLowerCase()) {
      case "admin":
        return "bg-purple-100 text-purple-800 border-purple-300";
      case "operator":
        return "bg-amber-100 text-amber-800 border-amber-300";
      default:
        return "bg-blue-100 text-blue-800 border-blue-300";
    }
  };

  return (
    <nav className="flex items-center justify-between bg-blue-700 px-6 py-3.5 text-white shadow-md">
      <div className="flex items-center gap-6">
        <Link href="/dashboard" className="text-xl font-bold tracking-tight flex items-center gap-2">
          <span>🚦</span>
          <span>TrafficVision AI</span>
        </Link>

        <div className="hidden md:flex gap-4 text-sm font-medium">
          <Link href="/dashboard" className="hover:text-blue-200 transition">
            Dashboard
          </Link>
          <Link href="/live-map" className="hover:text-blue-200 transition">
            Live Map
          </Link>
          <Link href="/alerts" className="hover:text-blue-200 transition">
            Alerts
          </Link>
          <Link href="/analytics" className="hover:text-blue-200 transition">
            Analytics
          </Link>
        </div>
      </div>

      <div className="flex items-center gap-4 text-sm">
        {isAuthenticated && user ? (
          <div className="flex items-center gap-3">
            <div className="flex flex-col items-end">
              <span className="font-semibold text-white leading-tight">{user.name}</span>
              <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${getRoleBadgeColor(role)} uppercase tracking-wider`}>
                {role}
              </span>
            </div>
            <button
              onClick={logout}
              className="rounded-lg bg-blue-800 px-3 py-1.5 text-xs font-semibold hover:bg-blue-900 transition border border-blue-600"
            >
              Logout
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="rounded-lg px-3 py-1.5 font-medium hover:text-blue-200 transition"
            >
              Login
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-white px-3.5 py-1.5 font-semibold text-blue-700 hover:bg-blue-50 transition shadow-sm"
            >
              Register
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}