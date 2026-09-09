"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function Navbar({ title }: { title: string }) {
  const router = useRouter();
  const [role, setRole] = useState("Public");

  useEffect(() => {
    const savedRole = localStorage.getItem("user_role");
    if (savedRole) setRole(savedRole);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("user_role");
    localStorage.removeItem("user_email");
    router.push("/login");
  };

  return (
    <header className="flex justify-between items-center py-4 px-2 border-b border-slate-800/60 mb-4">
      <h2 className="text-lg font-bold text-slate-200">{title}</h2>
      <div className="flex items-center gap-4">
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-cyan-950 text-cyan-400 border border-cyan-800">
          Active Mode: {role}
        </span>
        <button
          onClick={handleLogout}
          className="text-xs px-3 py-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20 transition"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
