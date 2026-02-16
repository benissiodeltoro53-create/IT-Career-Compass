import { useState } from "react";

const LEVELS = ["Trainee", "Junior", "Middle", "Senior"];

export default function Form({ onSubmit }) {
  const [level, setLevel] = useState("Junior");
  const [position, setPosition] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (position.trim()) {
      onSubmit(level, position.trim());
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="animate-fade-in bg-white/10 backdrop-blur-lg border border-white/20 rounded-3xl p-6 sm:p-10 shadow-2xl"
    >
      <label className="block text-indigo-200 text-sm font-medium mb-3">
        Рівень
      </label>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
        {LEVELS.map((l) => (
          <button
            key={l}
            type="button"
            onClick={() => setLevel(l)}
            className={`py-3 px-4 rounded-xl text-sm font-semibold transition-all duration-200 ${
              level === l
                ? "bg-indigo-500 text-white shadow-lg shadow-indigo-500/30 scale-105"
                : "bg-white/10 text-indigo-200 hover:bg-white/20"
            }`}
          >
            {l}
          </button>
        ))}
      </div>

      <label className="block text-indigo-200 text-sm font-medium mb-3">
        Позиція
      </label>
      <input
        type="text"
        value={position}
        onChange={(e) => setPosition(e.target.value)}
        placeholder="Наприклад: Frontend Developer, QA Engineer, Data Analyst..."
        className="w-full px-5 py-4 rounded-xl bg-white/10 border border-white/20 text-white placeholder-indigo-300/50 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent text-lg transition-all mb-8"
      />

      <button
        type="submit"
        disabled={!position.trim()}
        className="w-full py-4 rounded-xl text-lg font-bold transition-all duration-200 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white shadow-lg shadow-indigo-500/30 hover:shadow-xl hover:shadow-indigo-500/40 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:shadow-lg"
      >
        Показати roadmap
      </button>
    </form>
  );
}
