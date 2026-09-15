'use client';
import React from 'react';

export const Navbar: React.FC = () => {
  return (
    <nav className="w-full bg-[#161b22] border-b border-[#30363d] px-6 py-3 flex items-center justify-between text-white">
      <span className="font-bold tracking-wider">TrafficVision AI System</span>
      <span className="text-xs text-emerald-400 font-mono">● System Online</span>
    </nav>
  );
};
