"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "../lib/auth-context";
import { api } from "../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Please enter both email and password.");
      return;
    }

    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  }

  // Helper for one-click demo login
  async function handleDemoLogin(demoEmail: string, demoPass: string, demoRole: string, demoName: string) {
    setError("");
    setLoading(true);
    setEmail(demoEmail);
    setPassword(demoPass);

    try {
      // Attempt login directly
      await login(demoEmail, demoPass);
      router.push("/dashboard");
    } catch {
      // If user doesn't exist yet, auto-register then login
      try {
        await api.register(demoName, demoEmail, demoPass, demoRole);
        await login(demoEmail, demoPass);
        router.push("/dashboard");
      } catch (err: any) {
        setError(err.message || "Failed to initialize demo user");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-xl border border-gray-100">
        <div className="text-center mb-6">
          <div className="text-4xl mb-2">🚦</div>
          <h1 className="text-2xl font-bold text-gray-900">
            TrafficVision AI
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Smart Traffic Prediction & Congestion Management
          </p>
        </div>

        <h2 className="text-xl font-semibold text-gray-900 mb-5">
          Sign In
        </h2>

        {error && (
          <div className="mb-5 rounded-lg bg-red-50 p-3.5 text-sm text-red-700 border border-red-200">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="operator@trafficvision.ai"
              required
              className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-gray-900 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-gray-900 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition text-sm"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-blue-600 px-4 py-2.5 font-semibold text-white transition hover:bg-blue-700 disabled:opacity-50 text-sm shadow-sm"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        {/* Demo Accounts Quick-Login for Milestone 1 Walkthrough */}
        <div className="mt-6 pt-5 border-t border-gray-200">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2.5 text-center">
            Demo Walkthrough Quick-Login
          </p>
          <div className="grid grid-cols-3 gap-2 text-xs font-medium">
            <button
              type="button"
              onClick={() => handleDemoLogin("admin@trafficvision.ai", "Admin@123", "admin", "City Admin")}
              className="px-2 py-2 rounded-lg bg-purple-50 text-purple-700 border border-purple-200 hover:bg-purple-100 transition text-center font-semibold"
            >
              👑 Admin
            </button>
            <button
              type="button"
              onClick={() => handleDemoLogin("operator@trafficvision.ai", "Operator@123", "operator", "Traffic Operator")}
              className="px-2 py-2 rounded-lg bg-amber-50 text-amber-700 border border-amber-200 hover:bg-amber-100 transition text-center font-semibold"
            >
              🛠️ Operator
            </button>
            <button
              type="button"
              onClick={() => handleDemoLogin("commuter@trafficvision.ai", "Public@123", "public", "Commuter")}
              className="px-2 py-2 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 transition text-center font-semibold"
            >
              🚗 Public
            </button>
          </div>
        </div>

        <p className="mt-6 text-center text-sm text-gray-600">
          Don't have an account?{" "}
          <Link
            href="/register"
            className="font-semibold text-blue-600 hover:underline"
          >
            Create account
          </Link>
        </p>
      </div>
    </main>
  );
}