"use client";

import { useEffect, useMemo, useState } from "react";
import Navbar from "../components/Navbar";
import { apiUrl } from "../../lib/api";

type TaskOption = { id: string; name: string };
type LanguageOption = { id: string; name: string };

type ModelOption = {
  key: string;
  name: string;
  model_id: string;
  provider?: string;
  description?: string;
};

type ModelsResponse = {
  models: ModelOption[];
};

type BenchmarkResult = {
  id: number;
  status: string;
  ai_model: string;
  model_id?: string;
  code_source?: string;
  generation_warning?: string;
  compile_status: string;
  correctness?: number;
  security_issues?: number;
  security_scan_status?: string;
  quality_gate?: boolean;
  readability_score?: number;
  comment_density?: number;
  execution_time_ms?: number;
  code?: string;
  execution_output?: string | Record<string, unknown>;
  stdout?: string;
  stderr?: string;
  scores?: {
    correctness: string;
    security: string;
    readability: string;
  };
};

const TASK_OPTIONS: TaskOption[] = [
  { id: "A", name: "Read text file" },
  { id: "B", name: "Multi-threaded JSON read" },
  { id: "C", name: "Write text file" },
  { id: "D", name: "Multi-threaded JSON write" },
  { id: "E", name: "Create ZIP archive" },
  { id: "F", name: "MySQL query" },
  { id: "G", name: "MongoDB query" },
  { id: "H", name: "Password authentication" },
];

const LANGUAGE_OPTIONS: LanguageOption[] = [
  { id: "python", name: "Python" },
  { id: "javascript", name: "JavaScript" },
  { id: "php", name: "PHP" },
  { id: "bash", name: "Bash" },
];

export default function RunPage() {
  const [models, setModels] = useState<ModelOption[]>([]);
  const [selectedTask, setSelectedTask] = useState(TASK_OPTIONS[0].id);
  const [selectedModel, setSelectedModel] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState(LANGUAGE_OPTIONS[0].id);
  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState("Ready to benchmark.");
  const [latestResult, setLatestResult] = useState<BenchmarkResult | null>(null);
  const [expectedOutput, setExpectedOutput] = useState<Record<string, unknown> | null>(null);
  const [generatedCode, setGeneratedCode] = useState("Generated code will appear here after a run.");
  const [executionOutput, setExecutionOutput] = useState("Structured execution output will appear here after a run.");

  useEffect(() => {
    const fetchExpected = async () => {
      try {
        const res = await fetch(apiUrl(`/api/tasks/${selectedTask}/expected`));
        const data: Record<string, unknown> = await res.json();
        setExpectedOutput(data);
      } catch (error) {
        console.error("Failed to fetch expected output:", error);
      }
    };
    fetchExpected();
  }, [selectedTask]);

  useEffect(() => {
    let cancelled = false;

    async function loadModels() {
      try {
        const response = await fetch(apiUrl("/api/models"));
        if (!response.ok) {
          throw new Error("Failed to fetch model catalog");
        }

        const data: ModelsResponse = await response.json();
        if (!cancelled) {
          setModels(data.models || []);
          setSelectedModel((data.models && data.models[0]?.key) || "");
        }
      } catch (error) {
        console.error("Model fetch failed", error);
        if (!cancelled) {
          setStatus("Error: Unable to load model catalog from backend.");
        }
      }
    }

    loadModels();
    return () => {
      cancelled = true;
    };
  }, []);

  const currentModel = useMemo(
    () => models.find((model) => model.key === selectedModel),
    [models, selectedModel]
  );

  const handleRunBenchmark = async () => {
    if (!selectedModel) {
      setStatus("Error: Select a model first.");
      return;
    }

    setIsRunning(true);
    setStatus(`Running Task ${selectedTask} with ${selectedModel} (${selectedLanguage})...`);

    try {
      const response = await fetch(apiUrl("/api/benchmark"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          task_id: selectedTask,
          ai_model: selectedModel,
          language: selectedLanguage,
        }),
      });

      if (!response.ok) {
        const errorBody = (await response.json()) as { detail?: string };
        setLatestResult(null);
        setGeneratedCode("No generated code available for this run.");
        setExecutionOutput("No execution output available for this run.");
        setStatus(`Error: ${errorBody.detail || "Benchmark execution failed."}`);
        return;
      }

      const result: BenchmarkResult = await response.json();
      setLatestResult(result);
      setGeneratedCode(result.code || "No generated code returned.");
      setExecutionOutput(
        typeof result.execution_output === "string"
          ? result.execution_output
          : JSON.stringify(result.execution_output ?? {}, null, 2)
      );
      setStatus("Benchmark completed successfully.");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setLatestResult(null);
      setGeneratedCode("No generated code available for this run.");
      setExecutionOutput("No execution output available for this run.");
      setStatus(`System Error: ${message}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 p-8 font-sans text-neutral-100">
      <div className="mx-auto max-w-7xl space-y-6">
        <Navbar active="run" />

        {/* Top Section: Benchmark Configuration Bar */}
        <section className="rounded-2xl border border-neutral-800 bg-neutral-900 p-4 shadow-xl">
          <div className="flex flex-col items-end gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="grid w-full grid-cols-1 gap-4 sm:grid-cols-3 lg:w-auto lg:flex-1 lg:flex-row">
              <div className="flex-1">
                <label className="mb-1 block text-[10px] font-bold uppercase tracking-wider text-neutral-500">Task</label>
                <select
                  value={selectedTask}
                  onChange={(event) => setSelectedTask(event.target.value)}
                  className="w-full rounded-xl border border-neutral-800 bg-neutral-950 p-2.5 text-sm text-neutral-100 focus:border-indigo-500 focus:outline-none"
                >
                  {TASK_OPTIONS.map((task) => (
                    <option key={task.id} value={task.id}>
                      Task {task.id}: {task.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex-1">
                <label className="mb-1 block text-[10px] font-bold uppercase tracking-wider text-neutral-500">AI Model</label>
                <select
                  value={selectedModel}
                  onChange={(event) => setSelectedModel(event.target.value)}
                  className="w-full rounded-xl border border-neutral-800 bg-neutral-950 p-2.5 text-sm text-neutral-100 focus:border-indigo-500 focus:outline-none"
                  disabled={models.length === 0}
                >
                  {models.length === 0 ? <option value="">Loading...</option> : null}
                  {models.map((model) => (
                    <option key={model.key} value={model.key}>
                      {model.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex-1">
                <label className="mb-1 block text-[10px] font-bold uppercase tracking-wider text-neutral-500">Language</label>
                <select
                  value={selectedLanguage}
                  onChange={(event) => setSelectedLanguage(event.target.value)}
                  className="w-full rounded-xl border border-neutral-800 bg-neutral-950 p-2.5 text-sm text-neutral-100 focus:border-indigo-500 focus:outline-none"
                >
                  {LANGUAGE_OPTIONS.map((language) => (
                    <option key={language.id} value={language.id}>
                      {language.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex w-full flex-col gap-3 lg:w-72">
              <button
                onClick={handleRunBenchmark}
                disabled={isRunning || !selectedModel}
                className={`w-full rounded-xl border px-6 py-2.5 text-sm font-bold shadow-lg transition duration-200 ${
                  isRunning || !selectedModel
                    ? "cursor-not-allowed border-indigo-800/50 bg-indigo-900/50 text-indigo-300"
                    : "border-indigo-500 bg-indigo-600 text-white hover:scale-[1.02] hover:bg-indigo-500 active:scale-95"
                }`}
              >
                {isRunning ? "Running..." : "Run Benchmark"}
              </button>
            </div>
          </div>
          
          <div className="mt-4 flex flex-col justify-between gap-4 border-t border-neutral-800 pt-4 sm:flex-row sm:items-center">
             <div className="flex items-center gap-3">
               <div className={`h-2 w-2 rounded-full ${isRunning ? "animate-pulse bg-indigo-500" : "bg-emerald-500"}`}></div>
               <p className={`text-xs font-medium ${status.includes("Error") ? "text-red-400" : "text-neutral-400"}`}>
                 {status}
               </p>
             </div>
             {currentModel && (
               <p className="text-[10px] text-neutral-500 italic">
                 {currentModel.provider ? `${currentModel.provider} / ` : ""}{currentModel.model_id}
               </p>
             )}
          </div>
        </section>

        {/* Middle Section: Side-by-Side Code and Metrics */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Generated Code Section */}
          <section className="rounded-2xl border border-neutral-800 bg-neutral-900 p-6 shadow-xl">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-bold">Generated Code</h2>
              <span className="rounded-lg bg-neutral-950 px-2 py-1 text-[10px] font-mono text-neutral-500 border border-neutral-800">
                {selectedLanguage}
              </span>
            </div>
            {latestResult?.generation_warning ? (
              <div className="mb-4 rounded-lg border border-amber-800/30 bg-amber-950/20 px-3 py-2 text-xs text-amber-400">
                {latestResult.generation_warning}
              </div>
            ) : null}
            <div className="relative">
              <pre className="h-[400px] overflow-auto whitespace-pre-wrap rounded-xl border border-neutral-800 bg-neutral-950 p-4 font-mono text-xs leading-relaxed text-emerald-300 shadow-inner custom-scrollbar">
                {generatedCode}
              </pre>
            </div>
          </section>

          {/* Evaluation Metrics Section */}
          <section className="rounded-2xl border border-neutral-800 bg-neutral-900 p-6 shadow-xl">
            <h2 className="mb-6 text-xl font-bold">Evaluation Metrics</h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {[
                { label: "Correctness", value: latestResult?.scores?.correctness || (latestResult?.correctness !== undefined ? `${latestResult.correctness} / 1` : "—"), color: "text-indigo-400" },
                { label: "Status", value: latestResult?.compile_status, color: latestResult?.compile_status === "success" ? "text-emerald-400" : "text-red-400" },
                { label: "Readability", value: latestResult?.scores?.readability || "—", color: "text-sky-400" },
                { label: "Security", value: latestResult?.scores?.security || "—", color: (latestResult?.security_issues ?? 0) > 0 ? "text-red-400" : "text-emerald-400" },
                { label: "Comment %", value: latestResult?.comment_density, color: "text-neutral-300" },
                { label: "Time (ms)", value: latestResult?.execution_time_ms, color: "text-amber-400" },
              ].map((metric) => (
                <div key={metric.label} className="rounded-xl border border-neutral-800 bg-neutral-950 p-3 transition hover:border-neutral-700">
                  <p className="text-[10px] font-bold uppercase tracking-wider text-neutral-500">{metric.label}</p>
                  <p className={`mt-1 text-lg font-bold ${metric.color}`}>
                    {metric.value !== undefined && metric.value !== null ? String(metric.value) : "—"}
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-6 space-y-3">
              <div className="rounded-xl border border-neutral-800 bg-neutral-950 p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-neutral-400">Quality Gate</span>
                  <span className={`text-xs font-bold ${latestResult?.quality_gate ? "text-emerald-400" : "text-red-400"}`}>
                    {latestResult?.quality_gate ? "PASSED" : "FAILED"}
                  </span>
                </div>
                <div className="h-1.5 w-full rounded-full bg-neutral-900 overflow-hidden">
                  <div 
                    className={`h-full transition-all duration-1000 ${latestResult?.quality_gate ? "w-full bg-emerald-500" : "w-1/3 bg-red-500"}`}
                  ></div>
                </div>
              </div>
              
              <div className="rounded-xl border border-neutral-800 bg-neutral-950 p-3 text-[11px] text-neutral-500">
                <p>Scanner: {latestResult?.security_scan_status || "n/a"}</p>
                <p className="mt-1">Model: {latestResult?.model_id || "n/a"}</p>
              </div>
            </div>
          </section>
        </div>

        {/* Bottom Section: Side-by-Side Outputs */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Execution Output */}
          <section className="rounded-2xl border border-neutral-800 bg-neutral-900 p-6 shadow-xl">
            <div className="mb-4 flex items-center gap-2">
              <h2 className="text-xl font-bold">Execution Output</h2>
              <div className="h-1 flex-1 border-b border-neutral-800"></div>
            </div>
            <pre className="max-h-60 min-h-[150px] overflow-auto whitespace-pre-wrap rounded-xl border border-neutral-800 bg-neutral-950 p-5 font-mono text-xs leading-relaxed text-emerald-400 shadow-inner custom-scrollbar">
              {executionOutput}
            </pre>
          </section>

          {/* Expected Output (Ground Truth) */}
          <section className="rounded-2xl border border-neutral-800 bg-neutral-900 p-6 shadow-xl">
            <div className="mb-4 flex items-center gap-2">
              <h2 className="text-xl font-bold">Expected Output</h2>
              <div className="h-1 flex-1 border-b border-neutral-800"></div>
            </div>
            <pre className="max-h-60 min-h-[150px] overflow-auto whitespace-pre-wrap rounded-xl border border-neutral-800 bg-neutral-950 p-5 font-mono text-xs leading-relaxed text-sky-400 shadow-inner custom-scrollbar">
              {expectedOutput ? JSON.stringify(expectedOutput, null, 2) : "Loading task metadata..."}
            </pre>
          </section>
        </div>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
          height: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #0a0a0a;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #262626;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #404040;
        }
      `}</style>
    </div>
  );
}