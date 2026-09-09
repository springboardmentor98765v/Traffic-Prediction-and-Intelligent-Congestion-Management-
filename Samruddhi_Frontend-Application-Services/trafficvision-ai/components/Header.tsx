'use client';
import React from 'react';

interface HeaderProps {
  username?: string;
  role?: string;
}

export const Header: React.FC<HeaderProps> = ({ username = 'USER', role = 'Public' }) => {
  return (
    <header className="flex justify-between items-center mb-8 border-b border-[#30363d] pb-4">
      <div>
        <p className="text-xs text-[#58a6ff] uppercase tracking-wider font-semibold">
          WELCOME BACK, {username}
        </p>
        <h1 className="text-2xl font-bold">TrafficVision AI Platform</h1>
      </div>
      <div className="bg-[#161b22] border border-[#30363d] px-4 py-1.5 rounded-full text-xs font-semibold text-gray-300">
        Role: <span className="text-white">{role}</span>
      </div>
    </header>
  );
};
