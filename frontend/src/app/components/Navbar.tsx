type NavbarProps = {
  active?: "dashboard" | "run" | "history";
};

export default function Navbar({ active = "dashboard" }: NavbarProps) {
  const linkStyle = (name: "dashboard" | "run" | "history") =>
    `px-4 py-2 rounded-lg text-sm font-medium transition ${
      active === name
        ? "bg-purple-600 text-white"
        : "text-gray-300 hover:bg-gray-800 hover:text-white"
    }`;

  return (
    <nav className="w-full flex items-center justify-between border-b border-gray-800 pb-4 mb-8">
      <div>
        <h1 className="text-4xl font-bold text-purple-500">VibeBench</h1>
        <p className="text-gray-400 mt-1">Research Evaluating AI Coding Assistants</p>
      </div>

      <div className="flex items-center gap-3">
        <button className={linkStyle("dashboard")}>Dashboard</button>
        <button className={linkStyle("run")}>Run Benchmark</button>
        <button className={linkStyle("history")}>Results History</button>
      </div>
    </nav>
  );
}