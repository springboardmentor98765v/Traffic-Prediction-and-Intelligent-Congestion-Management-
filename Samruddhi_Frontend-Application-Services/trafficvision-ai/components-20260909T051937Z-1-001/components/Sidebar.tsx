'use client';
import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { LayoutDashboard, Map, BarChart3, AlertTriangle, LogOut } from 'lucide-react';

interface SidebarProps {
  role: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ role }) => {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem('userRole');
    localStorage.removeItem('username');
    router.push('/login');
  };

  return (
    <aside className="w-64 bg-[#161b22] border-r border-[#30363d] p-6 flex flex-col justify-between h-screen sticky top-0">
      <div>
        <h2 className="text-xl font-bold tracking-wide text-white mb-8">TrafficVision AI</h2>
        <nav className="space-y-2">
          <Link
            href="/dashboard"
            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
              pathname === '/dashboard' ? 'bg-[#1f6feb] text-white' : 'text-gray-400 hover:bg-[#21262d] hover:text-white'
            }`}
          >
            <LayoutDashboard size={18} /> Dashboard
          </Link>

          <Link
            href="/live-map"
            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
              pathname === '/live-map' ? 'bg-[#1f6feb] text-white' : 'text-gray-400 hover:bg-[#21262d] hover:text-white'
            }`}
          >
            <Map size={18} /> Live Map
          </Link>

          {(role === 'Operator' || role === 'Admin') && (
            <Link
              href="/incidents"
              className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
                pathname === '/incidents' ? 'bg-[#1f6feb] text-white' : 'text-gray-400 hover:bg-[#21262d] hover:text-white'
              }`}
            >
              <AlertTriangle size={18} /> Road Controls
            </Link>
          )}

          <Link
            href="/analytics"
            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
              pathname === '/analytics' ? 'bg-[#1f6feb] text-white' : 'text-gray-400 hover:bg-[#21262d] hover:text-white'
            }`}
          >
            <BarChart3 size={18} /> Analytics
          </Link>
        </nav>
      </div>

      <div className="pt-6 border-t border-[#30363d]">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-xs text-gray-400 uppercase font-semibold">Active Mode</p>
            <p className="text-sm font-bold text-[#58a6ff]">{role}</p>
          </div>
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 bg-[#da3633] hover:bg-[#f85149] text-white py-2 rounded-lg text-sm font-semibold transition-all"
        >
          <LogOut size={16} /> Logout
        </button>
      </div>
    </aside>
  );
};
