const WEEK_ICONS = ["🚀", "📚", "💻", "🎯"];
const WEEK_LABELS = ["Тиждень 1", "Тиждень 2", "Тиждень 3", "Тиждень 4"];

export default function Results({ data, onReset }) {
  const { skills, roadmap, checklist } = data;

  return (
    <div className="animate-fade-in space-y-8">
      {/* Skills */}
      <section className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-3xl p-6 sm:p-8">
        <h2 className="text-2xl font-bold text-white mb-5 flex items-center gap-2">
          <span>🛠</span> Технічні навички
        </h2>
        <div className="flex flex-wrap gap-3">
          {skills.map((skill, i) => (
            <span
              key={i}
              className="px-4 py-2 bg-indigo-500/30 text-indigo-100 rounded-full text-sm font-medium border border-indigo-400/30"
            >
              {skill}
            </span>
          ))}
        </div>
      </section>

      {/* Roadmap */}
      <section className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-3xl p-6 sm:p-8">
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
          <span>🗺</span> Roadmap
        </h2>
        <div className="space-y-6">
          {Object.entries(roadmap).map(([week, tasks], wi) => (
            <div key={week} className="relative pl-8 border-l-2 border-indigo-500/40">
              <div className="absolute -left-3.5 top-0 w-7 h-7 bg-indigo-600 rounded-full flex items-center justify-center text-sm">
                {WEEK_ICONS[wi] || "📅"}
              </div>
              <h3 className="text-lg font-semibold text-indigo-200 mb-3">
                {WEEK_LABELS[wi] || week}
              </h3>
              <ul className="space-y-2">
                {tasks.map((task, ti) => (
                  <li
                    key={ti}
                    className="flex items-start gap-3 text-indigo-100/90"
                  >
                    <span className="mt-1.5 w-2 h-2 bg-purple-400 rounded-full shrink-0" />
                    {task}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* Checklist */}
      <section className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-3xl p-6 sm:p-8">
        <h2 className="text-2xl font-bold text-white mb-5 flex items-center gap-2">
          <span>✅</span> Checklist готовності
        </h2>
        <ul className="space-y-3">
          {checklist.map((item, i) => (
            <li key={i} className="flex items-start gap-3 text-indigo-100/90">
              <span className="mt-0.5 text-lg">☐</span>
              {item}
            </li>
          ))}
        </ul>
      </section>

      {/* Reset */}
      <div className="text-center pt-4 pb-8">
        <button
          onClick={onReset}
          className="px-8 py-4 rounded-xl text-lg font-bold transition-all duration-200 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white shadow-lg shadow-indigo-500/30 hover:shadow-xl"
        >
          Нова позиція
        </button>
      </div>
    </div>
  );
}
