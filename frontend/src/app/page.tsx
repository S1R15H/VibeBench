"use client";

import { useEffect, useState } from "react";
import Navbar from "./components/Navbar";
import StatCard from "./components/StatCard";
import { apiUrl } from "../lib/api";

type HealthResponse = {
  status: string;
  backend: string;
  database: {
    status: string;
    detail: string;
  };
  ready: boolean;
};

export default function Home() {
  const [totalRuns, setTotalRuns] = useState(0);
  const [modelCount, setModelCount] = useState(0);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const frontendStatus = "Running";

  useEffect(() => {
    async function loadDashboard() {
      try {
        const healthResponse = await fetch(apiUrl("/api/health"));
        if (healthResponse.ok) {
          const healthData: HealthResponse = await healthResponse.json();
          setHealth(healthData);
        }

        const resultsResponse = await fetch(apiUrl("/api/results"));
        if (resultsResponse.ok) {
          const results = await resultsResponse.json();
          setTotalRuns(Array.isArray(results) ? results.length : 0);
        }

        const modelsResponse = await fetch(apiUrl("/api/models"));
        if (modelsResponse.ok) {
          const payload = await modelsResponse.json();
          const models = Array.isArray(payload?.models) ? payload.models : [];
          setModelCount(models.length);
        }
      } catch (error) {
        console.error("Failed to load dashboard health", error);
      }
    }

    loadDashboard();
  }, []);

  const backendReady = health?.backend === "running";
  const databaseReady = health?.database.status === "connected";

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 font-sans p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <Navbar active="dashboard" />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Runs"
            value={String(totalRuns)}
            subtext="Benchmark records stored in SQLite"
          />
          <StatCard
            title="Models Tested"
            value={String(modelCount)}
            subtext="Configured model catalog from backend"
          />
          <StatCard
            title="Tasks Available"
            value="8"
            subtext="Research benchmark tasks"
          />
          <StatCard
            title="System Status"
            value={health?.ready ? "Ready" : "Checking"}
            subtext={health?.ready ? "Backend and database health checks passed" : "Waiting for backend and database health checks"}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-neutral-900 shadow-xl rounded-2xl p-6 border border-neutral-800">
            <h2 className="text-2xl font-bold mb-4">Dashboard Overview</h2>
            <p className="text-neutral-400 leading-7">
              VibeBench is a benchmarking framework for evaluating AI-based coding
              assistants across correctness, security, readability, and
              performance. Use the navigation bar to start a benchmark run or
              review experiment history.
            </p>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-4">
                <p className="text-sm text-neutral-400">Quick Access</p>
                <p className="text-white mt-1 font-medium">Run a new benchmark from the Run Benchmark page</p>
              </div>

              <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-4">
                <p className="text-sm text-neutral-400">History</p>
                <p className="text-white mt-1 font-medium">Review previous runs from the Results History page</p>
              </div>
            </div>
          </div>

          <div className="bg-neutral-900 shadow-xl rounded-2xl p-6 border border-neutral-800">
            <h2 className="text-xl font-bold mb-4">Current Status</h2>
            <div className="space-y-4">
              <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-4">
                <p className="text-sm text-neutral-400">Frontend</p>
                <p className="text-green-400 font-medium mt-1">{frontendStatus}</p>
              </div>

              <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-4">
                <p className="text-sm text-neutral-400">Backend API</p>
                <p className={backendReady ? "text-green-400 font-medium mt-1" : "text-yellow-400 font-medium mt-1"}>
                  {backendReady ? "Connected" : "Checking"}
                </p>
                {health?.database.detail ? <p className="mt-2 text-xs text-neutral-500">{health.database.detail}</p> : null}
              </div>

              <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-4">
                <p className="text-sm text-neutral-400">Database</p>
                <p className={databaseReady ? "text-green-400 font-medium mt-1" : "text-yellow-400 font-medium mt-1"}>
                  {databaseReady ? "Connected" : "Checking"}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}