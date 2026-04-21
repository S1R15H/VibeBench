"use client";

import Navbar from "./components/Navbar";
import StatCard from "./components/StatCard";

export default function Home() {
  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 font-sans p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <Navbar active="dashboard" />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Runs"
            value="0"
            subtext="Benchmark records stored"
          />
          <StatCard
            title="Models Tested"
            value="5"
            subtext="GPT-4, Claude, Gemini, Copilot"
          />
          <StatCard
            title="Tasks Available"
            value="8"
            subtext="Research benchmark tasks"
          />
          <StatCard
            title="System Status"
            value="Ready"
            subtext="Frontend and backend connected"
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
                <p className="text-green-400 font-medium mt-1">Running</p>
              </div>

              <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-4">
                <p className="text-sm text-neutral-400">Backend API</p>
                <p className="text-green-400 font-medium mt-1">Connected</p>
              </div>

              <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-4">
                <p className="text-sm text-neutral-400">Database</p>
                <p className="text-green-400 font-medium mt-1">Initialized</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}