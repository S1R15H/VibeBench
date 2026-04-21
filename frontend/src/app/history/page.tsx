"use client";

import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";

export default function HistoryPage() {
  const [results, setResults] = useState<any[]>([]);

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/results");
      if (response.ok) {
        const data = await response.json();
        setResults(data);
      }
    } catch (e) {
      console.error("Failed to fetch results", e);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 font-sans p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <Navbar active="history" />

        <div className="bg-neutral-900 shadow-xl rounded-2xl p-6 border border-neutral-800">
          <h2 className="text-2xl font-bold mb-4">Results History</h2>
          <p className="text-neutral-400 mb-6">
            This page shows saved benchmark runs from the local database.
          </p>

          <div className="overflow-auto rounded-xl border border-neutral-800 bg-neutral-950">
            {results.length === 0 ? (
              <div className="p-8 text-center text-neutral-500">
                No benchmark history available yet.
              </div>
            ) : (
              <table className="w-full text-sm text-left text-neutral-300">
                <thead className="text-xs text-neutral-400 uppercase bg-neutral-900/80 border-b border-neutral-800">
                  <tr>
                    <th className="px-5 py-4 font-semibold">Run ID</th>
                    <th className="px-5 py-4 font-semibold">Model</th>
                    <th className="px-5 py-4 font-semibold">Task</th>
                    <th className="px-5 py-4 font-semibold">Status</th>
                    <th className="px-5 py-4 font-semibold text-center">Issues</th>
                    <th className="px-5 py-4 font-semibold text-center">Readability</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-800/50">
                  {results.map((r) => (
                    <tr key={r.id} className="hover:bg-neutral-800/30 transition-colors">
                      <td className="px-5 py-4 font-mono text-neutral-400">#{r.id}</td>
                      <td className="px-5 py-4 font-medium text-indigo-300">{r.ai_model}</td>
                      <td className="px-5 py-4">Task {r.task_id}</td>
                      <td className="px-5 py-4">{r.compile_status}</td>
                      <td className="px-5 py-4 text-center">{r.security_issues}</td>
                      <td className="px-5 py-4 text-center">
                        {r.readability_score > 0 ? r.readability_score : "-"}
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