'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Dashboard', href: '/dashboard' },
    { name: 'Live Map', href: '/map' },
    { name: 'Incidents', href: '/incidents' },
    { name: 'Analytics', href: '/analytics' },
  ];

  return (
    <aside className="w-64 bg-[#090d16] border-r border-slate-800/80 min-h-screen p-6 flex flex-col justify-between shrink-0">
      <div>
        {/* Brand Logo */}
        <div className="mb-10">
          <h1 className="text-xl font-black text-cyan-400 tracking-tight flex items-center gap-2">
            TrafficVision AI
          </h1>
        </div>

        {/* Navigation Links */}
        <nav className="space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`block px-4 py-3 rounded-xl text-xs font-bold transition-all ${
                  isActive
                    ? 'bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-400/20'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
                }`}
              >
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Version Tag */}
      <div className="text-[10px] text-slate-600 font-semibold">
        Version 1.0.0
      </div>
    </aside>
  );
}
