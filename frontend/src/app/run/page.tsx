"use client";

import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";

export default function RunPage() {
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

  const handleClearForm = () => {
    setCodeSnippet("");
    setSelectedTask(tasks[0].id);
    setSelectedModel(models[0].id);
    setSelectedLanguage(languages[0].id);
    setStatus("Form cleared.");
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 font-sans p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <Navbar active="run" />

        <main className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-neutral-900 shadow-xl rounded-2xl p-6 border border-neutral-800">
              <h2 className="text-xl font-bold mb-6">Benchmark Configuration</h2>

              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold text-neutral-300 mb-2">
                    Research Task
                  </label>
                  <p className="text-xs text-neutral-500 mb-2">
                    Select the benchmark task to evaluate.
                  </p>
                  <select
                    value={selectedTask}
                    onChange={(e) => setSelectedTask(e.target.value)}
                    className="w-full bg-neutral-950 border border-neutral-800 text-neutral-100 text-sm rounded-xl p-3"
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
                    <p className="text-xs text-neutral-500 mb-2">
                      Choose the assistant being evaluated.
                    </p>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="w-full bg-neutral-950 border border-neutral-800 text-neutral-100 text-sm rounded-xl p-3"
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
                    <p className="text-xs text-neutral-500 mb-2">
                      Select the generated code language.
                    </p>
                    <select
                      value={selectedLanguage}
                      onChange={(e) => setSelectedLanguage(e.target.value)}
                      className="w-full bg-neutral-950 border border-neutral-800 text-neutral-100 text-sm rounded-xl p-3"
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
                  <label className="block text-sm font-semibold text-neutral-300 mb-2">
                    Generated Code Snippet
                  </label>
                  <p className="text-xs text-neutral-500 mb-2">
                    Paste the AI-generated code here before running the benchmark.
                  </p>
                  <textarea
                    value={codeSnippet}
                    onChange={(e) => setCodeSnippet(e.target.value)}
                    rows={12}
                    className="w-full bg-neutral-950 border border-neutral-800 text-neutral-200 text-sm rounded-xl p-4 font-mono leading-relaxed resize-y"
                    placeholder="// Paste the code generated by the AI model here..."
                  ></textarea>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={handleRunBenchmark}
                    disabled={isRunning}
                    className={`w-full py-3 px-4 text-sm font-bold rounded-xl transition ${
                      isRunning
                        ? "bg-indigo-900/50 text-indigo-300 cursor-not-allowed border border-indigo-800/50"
                        : "bg-indigo-600 hover:bg-indigo-500 text-white border border-indigo-500"
                    }`}
                  >
                    {isRunning ? "Executing Pipeline..." : "Run Benchmark"}
                  </button>

                  <button
                    onClick={handleClearForm}
                    className="w-full py-3 px-4 text-sm font-bold rounded-xl bg-neutral-800 hover:bg-neutral-700 text-white border border-neutral-700"
                  >
                    Clear Form
                  </button>
                </div>

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

          <div className="lg:col-span-7 space-y-6">
            <div className="bg-neutral-900 shadow-xl rounded-2xl p-6 border border-neutral-800 h-full flex flex-col">
              <h2 className="text-xl font-bold mb-6">Recent Experiment History</h2>

              <div className="flex-grow overflow-auto rounded-xl border border-neutral-800 bg-neutral-950">
                {results.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-64 text-neutral-500">
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
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-neutral-800/50">
                      {results.map((r) => (
                        <tr key={r.id} className="hover:bg-neutral-800/30 transition-colors">
                          <td className="px-5 py-4 font-mono text-neutral-400">#{r.id}</td>
                          <td className="px-5 py-4 font-medium text-indigo-300">{r.ai_model}</td>
                          <td className="px-5 py-4">Task {r.task_id}</td>
                          <td className="px-5 py-4">{r.compile_status}</td>
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