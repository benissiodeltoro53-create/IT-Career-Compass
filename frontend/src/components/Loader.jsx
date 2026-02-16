export default function Loader() {
  return (
    <div className="animate-fade-in flex flex-col items-center justify-center py-20">
      <div className="flex space-x-3 mb-6">
        <span className="loader-dot w-4 h-4 bg-indigo-400 rounded-full inline-block" />
        <span className="loader-dot w-4 h-4 bg-purple-400 rounded-full inline-block" />
        <span className="loader-dot w-4 h-4 bg-indigo-400 rounded-full inline-block" />
      </div>
      <p className="text-indigo-300 text-lg">Claude аналізує ринок та готує roadmap...</p>
    </div>
  );
}
