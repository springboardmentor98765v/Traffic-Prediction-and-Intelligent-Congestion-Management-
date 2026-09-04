export default function Home() {
  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold text-blue-700">
        TrafficVision AI
      </h1>

      <p className="mt-2 text-gray-600">
        Smart Traffic Prediction & Congestion Management System
      </p>

      <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="rounded-xl bg-white p-6 shadow">
          <h2 className="text-lg font-semibold">Traffic Status</h2>
          <p className="mt-2 text-green-600">Normal</p>
        </div>

        <div className="rounded-xl bg-white p-6 shadow">
          <h2 className="text-lg font-semibold">Congestion Level</h2>
          <p className="mt-2 text-yellow-600">Medium</p>
        </div>

        <div className="rounded-xl bg-white p-6 shadow">
          <h2 className="text-lg font-semibold">Prediction</h2>
          <p className="mt-2 text-blue-600">Coming Soon</p>
        </div>
      </div>
    </main>
  );
}