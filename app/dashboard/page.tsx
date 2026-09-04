"use client";

import { useState } from "react";
import Layout from "../components/Layout";
import ErrorMessage from "../components/ErrorMessage";
import Card from "../components/Card";

export default function DashboardPage() {
  const [role, setRole] = useState("Operator");

  return (
    <Layout>
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">
            Dashboard
          </h1>

          <p className="mt-2 text-gray-600">
            Welcome to TrafficVision AI
          </p>
        </div>

        {/* Role Selection */}
        <div className="rounded-lg bg-white p-3 shadow">
          <label className="mr-3 text-sm font-medium text-gray-700">
            User Role:
          </label>

          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-800 outline-none focus:border-blue-600"
          >
            <option value="Operator">Operator</option>
            <option value="Admin">Admin</option>
          </select>
        </div>
      </div>

      {/* Error Message */}
      <div className="mt-6">
        <ErrorMessage message="Traffic data is currently unavailable. Showing demo data." />
      </div>

      {/* Role Panel */}
      <div className="mt-6 rounded-xl border border-blue-200 bg-blue-50 p-5">
        <h2 className="text-lg font-bold text-blue-800">
          {role} Panel
        </h2>

        <p className="mt-1 text-sm text-blue-700">
          {role === "Admin"
            ? "Admin can monitor traffic, alerts and system information."
            : "Operator can monitor live traffic, congestion and alerts."}
        </p>
      </div>

      {/* KPI Cards */}
      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card
          title="Traffic Status"
          value="Normal"
          valueClassName="text-green-600"
        />

        <Card
          title="Congestion Level"
          value="Medium"
          valueClassName="text-yellow-600"
        />

        <Card
          title="Active Alerts"
          value={3}
          valueClassName="text-red-600"
        />

        <Card
          title="Prediction"
          value="Available"
          valueClassName="text-blue-600"
        />
      </div>

      {/* Traffic Prediction */}
      <div className="mt-8 rounded-xl bg-white p-6 shadow">
        <h2 className="text-xl font-bold text-gray-800">
          Traffic Prediction
        </h2>

        <p className="mt-2 text-gray-600">
          AI-based traffic prediction for selected roads.
        </p>

        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-gray-200 p-5">
            <h3 className="font-semibold text-gray-700">
              Main Road
            </h3>

            <p className="mt-2 text-sm text-gray-500">
              Expected congestion
            </p>

            <p className="mt-2 font-bold text-red-600">
              High
            </p>
          </div>

          <div className="rounded-lg border border-gray-200 p-5">
            <h3 className="font-semibold text-gray-700">
              Central Junction
            </h3>

            <p className="mt-2 text-sm text-gray-500">
              Expected congestion
            </p>

            <p className="mt-2 font-bold text-yellow-600">
              Medium
            </p>
          </div>

          <div className="rounded-lg border border-gray-200 p-5">
            <h3 className="font-semibold text-gray-700">
              Airport Road
            </h3>

            <p className="mt-2 text-sm text-gray-500">
              Expected congestion
            </p>

            <p className="mt-2 font-bold text-green-600">
              Low
            </p>
          </div>
        </div>
      </div>

      {/* Admin Controls */}
      {role === "Admin" && (
        <div className="mt-8 rounded-xl bg-white p-6 shadow">
          <h2 className="text-xl font-bold text-gray-800">
            Admin Controls
          </h2>

          <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-gray-200 p-5">
              <h3 className="font-semibold text-gray-700">
                User Management
              </h3>

              <p className="mt-2 text-sm text-gray-500">
                Manage system users and roles.
              </p>
            </div>

            <div className="rounded-lg border border-gray-200 p-5">
              <h3 className="font-semibold text-gray-700">
                System Monitoring
              </h3>

              <p className="mt-2 text-sm text-gray-500">
                Monitor traffic system activity.
              </p>
            </div>

            <div className="rounded-lg border border-gray-200 p-5">
              <h3 className="font-semibold text-gray-700">
                Reports
              </h3>

              <p className="mt-2 text-sm text-gray-500">
                View traffic and congestion reports.
              </p>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}