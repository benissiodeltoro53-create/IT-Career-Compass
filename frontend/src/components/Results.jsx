export default function Results({ data, onReset }) {
  const { title, steps } = data;

  return (
    <div className="animate-fade-in space-y-8">
      {/* Title */}
      <section className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-3xl p-6 sm:p-8">
        <h2 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
          <span>🗺️</span> {title}
        </h2>
      </section>

      {/* Roadmap Steps */}
      <section className="space-y-6">
        {steps.map((step, index) => (
          <div
            key={index}
            className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-3xl p-6 sm:p-8 relative"
          >
            {/* Month badge */}
            <div className="absolute -top-4 left-6 px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full text-white font-bold text-sm shadow-lg">
              Місяць {step.month}
            </div>

            <div className="mt-2">
              <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                {step.title}
              </h3>

              <p className="text-indigo-200 mb-6 leading-relaxed">
                {step.description}
              </p>

              {/* Skills */}
              {step.skills && step.skills.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-indigo-300 mb-3 flex items-center gap-2">
                    <span>🛠️</span> Навички
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {step.skills.map((skill, i) => (
                      <span
                        key={i}
                        className="px-3 py-1.5 bg-indigo-500/30 text-indigo-100 rounded-full text-sm font-medium border border-indigo-400/30"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Resources */}
              {step.resources && step.resources.length > 0 && (
                <div>
                  <h4 className="text-lg font-semibold text-purple-300 mb-3 flex items-center gap-2">
                    <span>📚</span> Ресурси
                  </h4>
                  <ul className="space-y-2">
                    {step.resources.map((resource, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-3 text-purple-100/90"
                      >
                        <span className="mt-1.5 w-2 h-2 bg-purple-400 rounded-full shrink-0" />
                        {resource}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
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