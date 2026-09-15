"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "../lib/auth-context";

export default function Sidebar() {
  const pathname = usePathname();
  const { user, role, isAuthenticated, logout } = useAuth();

  const links = [
    { href: "/dashboard", label: "Dashboard", icon: "📊" },
    { href: "/live-map", label: "Live Traffic Map", icon: "🗺️" },
    { href: "/alerts", label: "Traffic Alerts", icon: "🚨" },
    { href: "/analytics", label: "Analytics (M2/M3)", icon: "📈" },
  ];

  return (
    <aside className="w-full md:w-64 min-h-auto md:min-h-screen bg-white border-r border-gray-200 p-5 flex flex-col justify-between">
      <div>
        <div className="mb-6 pb-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🚦</span>
            <div>
              <h2 className="text-lg font-bold text-gray-900 leading-tight">
                TrafficVision AI
              </h2>
              <p className="text-xs text-gray-500 font-medium">
                Milestone 1 Increment
              </p>
            </div>
          </div>

          {isAuthenticated && user && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200 text-xs">
              <div className="text-gray-500">Active User:</div>
              <div className="font-semibold text-gray-800 truncate">{user.name}</div>
              <div className="mt-1 inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-blue-100 text-blue-800">
                {role}
              </div>
            </div>
          )}
        </div>

        <nav className="space-y-1.5">
          {links.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-lg px-3.5 py-2.5 text-sm font-medium transition ${
                  isActive
                    ? "bg-blue-600 text-white shadow-sm"
                    : "text-gray-700 hover:bg-gray-100"
                }`}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="pt-6 mt-6 border-t border-gray-100 space-y-2">
        {isAuthenticated ? (
          <button
            onClick={logout}
            className="w-full flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition"
          >
            <span>🚪</span>
            <span>Sign Out</span>
          </button>
        ) : (
          <div className="space-y-2">
            <Link
              href="/login"
              className="block text-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 transition"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="block text-center rounded-lg border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50 transition"
            >
              Create Account
            </Link>
          </div>
        )}
      </div>
    </aside>
  );
}