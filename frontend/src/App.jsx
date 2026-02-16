import { useState } from "react";
import Form from "./components/Form";
import Results from "./components/Results";
import Loader from "./components/Loader";

const API_URL = import.meta.env.VITE_API_URL || "";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(level, position) {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/generate-roadmap`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ level, position }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Server error ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setResult(null);
    setError(null);
  }

  return (
    <div className="min-h-screen flex flex-col items-center px-4 py-8 sm:py-16">
      <header className="text-center mb-10 animate-fade-in">
        <h1 className="text-4xl sm:text-5xl font-bold text-white mb-3 tracking-tight">
          <span className="mr-2">🧭</span>IT Career Compass
        </h1>
        <p className="text-indigo-300 text-lg sm:text-xl max-w-xl mx-auto">
          Персональний roadmap для твоєї IT-кар'єри за стандартами DOU та Djinni
        </p>
      </header>

      <main className="w-full max-w-3xl">
        {!result && !loading && (
          <Form onSubmit={handleSubmit} />
        )}

        {loading && <Loader />}

        {error && (
          <div className="animate-fade-in bg-red-500/20 border border-red-500/40 rounded-2xl p-6 text-center">
            <p className="text-red-300 text-lg mb-4">{error}</p>
            <button
              onClick={handleReset}
              className="px-6 py-3 bg-red-500/30 hover:bg-red-500/50 text-white rounded-xl transition-colors"
            >
              Спробувати ще раз
            </button>
          </div>
        )}

        {result && <Results data={result} onReset={handleReset} />}
      </main>

      <footer className="mt-auto pt-12 pb-4 text-indigo-400/60 text-sm">
        IT Career Compass &copy; {new Date().getFullYear()}
      </footer>
    </div>
  );
}
