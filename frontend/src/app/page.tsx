"use client";

import { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import StatCard from "./components/StatCard";

export default function Home() {
  const [tasks] = useState([
    { id: "A", name: "Read text file" },
    { id: "B", name: "Multi-threaded JSON read" },
    { id: "C", name: "Write text file" },
    { id: "D", name: "Multi-threaded JSON write" },
    { id: "E", name: "Create ZIP archive" },
    { id: "F", name: "MySQL query" },
    { id: "G", name: "MongoDB query" },
    { id: "H", name: "Password authentication (JS/PHP)" },
  ]);

  const [models] = useState([
    { id: "gpt-4-turbo", name: "GPT-4 Turbo" },
    { id: "claude-3-opus", name: "Claude 3 Opus" },
    { id: "claude-3-sonnet", name: "Claude 3 Sonnet" },
    { id: "gemini-1.5-pro", name: "Gemini 1.5 Pro" },
    { id: "github-copilot", name: "GitHub Copilot (Manual)" },
  ]);

  const [languages] = useState([
    { id: "python", name: "Python" },
    { id: "javascript", name: "JavaScript" },
    { id: "php", name: "PHP" },
  ]);

  const [selectedTask, setSelectedTask] = useState(tasks[0].id);
  const [selectedModel, setSelectedModel] = useState(models[0].id);
  const [selectedLanguage, setSelectedLanguage] = useState(languages[0].id);
  const [codeSnippet, setCodeSnippet] = useState("");

  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState("Ready to benchmark.");
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

  const handleRunBenchmark = async () => {
    if (!codeSnippet.trim()) {
      setStatus("Error: Please provide code to benchmark.");
      return;
    }

    setIsRunning(true);
    setStatus(`Running benchmark for Task ${selectedTask} on ${selectedModel}...`);

    try {
      const response = await fetch("http://localhost:8000/api/benchmark", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          task_id: selectedTask,
          ai_model: selectedModel,
          language: selectedLanguage,
          code: codeSnippet,
        }),
      });

      if (response.ok) {
        setStatus("Benchmark completed successfully.");
        setCodeSnippet("");
        await fetchResults();
      } else {
        const errData = await response.json();
        setStatus(`Error: ${errData.detail || "Execution failed"}`);
      }
    } catch (error: any) {
      setStatus(`System Error: ${error.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      const resp = await fetch("http://localhost:8000/api/export/csv");
      if (resp.ok) {
        setStatus("Successfully exported to results.csv on the backend.");
      }
    } catch (e) {
      setStatus("Failed to export CSV.");
    }
  };
    return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 font-sans p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <Navbar active="dashboard" />

        <div className="flex justify-end gap-4 -mt-2">
          <button
            onClick={handleExportCSV}
            className="px-5 py-2.5 bg-neutral-800 hover:bg-neutral-700 text-sm font-semibold rounded-lg shadow transition-colors border border-neutral-700"
          >
            Export CSV
          </button>
          <div className="px-5 py-2.5 bg-green-950/40 text-green-400 text-sm font-semibold rounded-lg shadow border border-green-900/50 flex items-center">
            API Connected
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Runs"
            value={String(results.length)}
            subtext="Benchmark records stored"
          />
          <StatCard
            title="Models Tested"
            value="5"
            subtext="GPT-4, Claude, Gemini, Copilot"
          />
          <StatCard
            title="Tasks Available"
            value={String(tasks.length)}
            subtext="Research benchmark tasks"
          />
          <StatCard
            title="Current Status"
            value={isRunning ? "Running" : "Idle"}
            subtext={status}
          />
        </div>

        <main className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                  <div className="lg:col-span-5 space-y-6">
            <div className="bg-neutral-900 shadow-xl rounded-2xl p-6 border border-neutral-800">
              <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 text-indigo-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z"
                    clipRule="evenodd"
                  />
                </svg>
                Benchmark Configuration
              </h2>

              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold text-neutral-300 mb-2">
                    Research Task
                  </label>
                  <select
                    value={selectedTask}
                    onChange={(e) => setSelectedTask(e.target.value)}
                    className="w-full bg-neutral-950 border border-neutral-800 text-neutral-100 text-sm rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 block p-3 transition-shadow"
                  >
                    {tasks.map((t) => (
                      <option key={t.id} value={t.id}>
                        Task {t.id}: {t.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-neutral-300 mb-2">
                      AI Model
                    </label>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="w-full bg-neutral-950 border border-neutral-800 text-neutral-100 text-sm rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 block p-3 transition-shadow"
                    >
                      {models.map((m) => (
                        <option key={m.id} value={m.id}>
                          {m.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-neutral-300 mb-2">
                      Language
                    </label>
                    <select
                      value={selectedLanguage}
                      onChange={(e) => setSelectedLanguage(e.target.value)}
                      className="w-full bg-neutral-950 border border-neutral-800 text-neutral-100 text-sm rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 block p-3 transition-shadow"
                    >
                      {languages.map((l) => (
                        <option key={l.id} value={l.id}>
                          {l.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-neutral-300 mb-2 flex justify-between">
                    Generated Code Snippet
                    <span className="text-xs text-neutral-500 font-normal">
                      Paste AI output here
                    </span>
                  </label>
                  <textarea
                    value={codeSnippet}
                    onChange={(e) => setCodeSnippet(e.target.value)}
                    rows={12}
                    className="w-full bg-neutral-950 border border-neutral-800 text-neutral-200 text-sm rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 block p-4 font-mono leading-relaxed transition-shadow resize-y"
                    placeholder="// Paste the code generated by the AI model here..."
                  ></textarea>
                </div>

                <div className="pt-2">
                  <button
                    onClick={handleRunBenchmark}
                    disabled={isRunning}
                    className={`w-full py-3.5 px-4 text-sm font-bold rounded-xl shadow-lg transition-all duration-200 flex justify-center items-center gap-2 ${
                      isRunning
                        ? "bg-indigo-900/50 text-indigo-300 cursor-not-allowed border border-indigo-800/50"
                        : "bg-indigo-600 hover:bg-indigo-500 text-white hover:shadow-indigo-500/25 border border-indigo-500"
                    }`}
                  >
                    {isRunning ? (
                      <>
                        <svg
                          className="animate-spin -ml-1 mr-2 h-4 w-4 text-indigo-300"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                        >
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                          ></circle>
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          ></path>
                        </svg>
                        Executing Pipeline...
                      </>
                    ) : (
                      <>
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-5 w-5"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
                            clipRule="evenodd"
                          />
                        </svg>
                        Run Benchmark
                      </>
                    )}
                  </button>

                  <div className="mt-4 text-center">
                    <p
                      className={`text-sm font-medium px-4 py-2 rounded-lg inline-block ${
                        status.includes("Error")
                          ? "text-red-400 bg-red-950/30"
                          : status.includes("success")
                          ? "text-green-400 bg-green-950/30"
                          : "text-neutral-400 bg-neutral-900/50"
                      }`}
                    >
                      {status}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="lg:col-span-7 space-y-6">
            <div className="bg-neutral-900 shadow-xl rounded-2xl p-6 border border-neutral-800 h-full flex flex-col">
              <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 text-purple-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path d="M5 4a1 1 0 00-2 0v7.268a2 2 0 000 3.464V16a1 1 0 102 0v-1.268a2 2 0 000-3.464V4zM11 4a1 1 0 10-2 0v1.268a2 2 0 000 3.464V16a1 1 0 102 0V8.732a2 2 0 000-3.464V4zM16 3a1 1 0 011 1v7.268a2 2 0 010 3.464V16a1 1 0 11-2 0v-1.268a2 2 0 010-3.464V4a1 1 0 011-1z" />
                </svg>
                Experiment History
              </h2>

              <div className="flex-grow overflow-auto rounded-xl border border-neutral-800 bg-neutral-950">
                {results.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-64 text-neutral-500">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-12 w-12 mb-3 opacity-20"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                      />
                    </svg>
                    <div className="text-center">
                      <p className="text-neutral-300 font-medium">No benchmark runs yet.</p>
                      <p className="text-sm text-neutral-500 mt-1">
                        Run your first benchmark to see results here.
                      </p>
                    </div>
                  </div>
                ) : (
                  <table className="w-full text-sm text-left text-neutral-300">
                    <thead className="text-xs text-neutral-400 uppercase bg-neutral-900/80 sticky top-0 border-b border-neutral-800">
                      <tr>
                        <th className="px-5 py-4 font-semibold">Run ID</th>
                        <th className="px-5 py-4 font-semibold">Model</th>
                        <th className="px-5 py-4 font-semibold">Task</th>
                        <th className="px-5 py-4 font-semibold">Status</th>
                        <th className="px-5 py-4 font-semibold text-center">Correct</th>
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
                              className={`inline-flex items-center justify-center h-6 min-w-[1.5rem] rounded-full px-2 text-xs font-bold ${
                                r.security_issues > 0
                                  ? "bg-red-500/10 text-red-400 shadow-[0_0_10px_rgba(248,113,113,0.1)]"
                                  : "bg-green-500/10 text-green-400"
                              }`}
                            >
                              {r.security_issues}
                            </span>
                          </td>
                          <td className="px-5 py-4 text-center font-mono text-xs text-neutral-400">
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
        </main>
      </div>
    </div>
  );
}