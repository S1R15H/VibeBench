"use client";

import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { apiUrl } from "../../lib/api";

type BenchmarkResult = {
  id: number;
  ai_model: string;
  model_id?: string;
  task_id: string;
  compile_status: string;
  functional_correctness: number;
  security_issues: number;
  readability_score: number;
  code?: string;
  execution_output?: string | Record<string, unknown>;
};

export default function HistoryPage() {
  const [results, setResults] = useState<BenchmarkResult[]>([]);
  const [status, setStatus] = useState("Loading history...");

  async function fetchResults() {
    try {
      const response = await fetch(apiUrl("/api/results"));
      if (response.ok) {
        const data: BenchmarkResult[] = await response.json();
        setResults(data);
        setStatus("Database connected.");
      } else {
        setStatus("Failed to load history.");
      }
    } catch (e) {
      console.error("Failed to fetch results", e);
      setStatus("Backend connection error.");
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchResults();
  }, []);

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 font-sans p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <Navbar active="history" />

        <div className="bg-neutral-900 shadow-xl rounded-2xl p-6 border border-neutral-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold">Results History</h2>
              <p className="text-neutral-400 mt-2">
                This page shows saved benchmark runs from the local database.
              </p>
            </div>

            <div className="flex items-center space-x-4">
              <a
                href={apiUrl("/api/export/csv")}
                className="text-sm px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition"
              >
                Export CSV
              </a>
              <div className="text-sm px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 text-neutral-400">
                {status}
              </div>
            </div>
          </div>

          <div className="overflow-auto rounded-xl border border-neutral-800 bg-neutral-950">
            {results.length === 0 ? (
              <div className="p-10 text-center text-neutral-500">
                <p className="text-neutral-300 font-medium">No benchmark history available yet.</p>
                <p className="text-sm text-neutral-500 mt-1">
                  Run a benchmark first, then results will appear here.
                </p>
              </div>
            ) : (
              <table className="w-full text-sm text-left text-neutral-300">
                <thead className="text-xs text-neutral-400 uppercase bg-neutral-900/80 border-b border-neutral-800">
                  <tr>
                    <th className="px-5 py-4 font-semibold">Run ID</th>
                    <th className="px-5 py-4 font-semibold">Model</th>
                    <th className="px-5 py-4 font-semibold">Task</th>
                    <th className="px-5 py-4 font-semibold">Status</th>
                    <th className="px-5 py-4 font-semibold text-center">Correct</th>
                    <th className="px-5 py-4 font-semibold text-center">Issues</th>
                    <th className="px-5 py-4 font-semibold text-center">Readability</th>
                    <th className="px-5 py-4 font-semibold">Code</th>
                    <th className="px-5 py-4 font-semibold">Output</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-800/50">
                  {results.map((r) => (
                    <tr
                      key={r.id}
                      className="hover:bg-neutral-800/30 transition-colors cursor-pointer"
                    >
                      <td className="px-5 py-4 font-mono text-neutral-400">#{r.id}</td>
                      <td className="px-5 py-4 font-medium text-indigo-300">{r.ai_model}</td>
                      <td className="px-5 py-4">Task {r.task_id}</td>
                      <td className="px-5 py-4">
                        <span
                          className={`px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider ${
                            r.compile_status === "success"
                              ? "bg-green-900/30 text-green-400 border border-green-800/50"
                              : r.compile_status === "warning"
                              ? "bg-yellow-900/30 text-yellow-500 border border-yellow-800/50"
                              : "bg-red-900/30 text-red-400 border border-red-800/50"
                          }`}
                        >
                          {r.compile_status}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-center">
                        {r.functional_correctness === 1.0 ? (
                          <span className="text-green-500 font-bold">✓</span>
                        ) : (
                          <span className="text-red-500 font-bold">✗</span>
                        )}
                      </td>
                      <td className="px-5 py-4 text-center">
                        <span
                          className={`inline-flex items-center justify-center h-6 min-w-6 rounded-full px-2 text-xs font-bold ${
                            r.security_issues > 0
                              ? "bg-red-500/10 text-red-400"
                              : "bg-green-500/10 text-green-400"
                          }`}
                        >
                          {r.security_issues}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-center font-mono text-xs text-neutral-400">
                        {r.readability_score > 0 ? r.readability_score : "-"}
                      </td>
                      <td className="px-5 py-4 align-top">
                        <details className="group">
                          <summary className="cursor-pointer list-none text-indigo-300 hover:text-indigo-200">View</summary>
                          <pre className="mt-3 max-w-md overflow-auto whitespace-pre-wrap wrap-break-word rounded-lg bg-black/40 p-3 text-[11px] leading-relaxed text-emerald-200 font-mono">
                            {r.code || "No code stored."}
                          </pre>
                        </details>
                      </td>
                      <td className="px-5 py-4 align-top">
                        <details className="group">
                          <summary className="cursor-pointer list-none text-indigo-300 hover:text-indigo-200">View</summary>
                          <pre className="mt-3 max-w-md overflow-auto whitespace-pre-wrap wrap-break-word rounded-lg bg-black/40 p-3 text-[11px] leading-relaxed text-neutral-200 font-mono">
                            {typeof r.execution_output === "string" 
                              ? r.execution_output 
                              : JSON.stringify(r.execution_output || {}, null, 2)}
                          </pre>
                        </details>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}