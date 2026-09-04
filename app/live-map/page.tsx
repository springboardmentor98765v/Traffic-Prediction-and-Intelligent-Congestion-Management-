export default function LiveMapPage() {
  return (
    <main className="min-h-screen bg-gray-100 p-6 md:p-8">

      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800">
          Live Traffic Map
        </h1>

        <p className="mt-2 text-gray-600">
          Monitor current traffic conditions and congestion levels.
        </p>
      </div>

      {/* Traffic Summary */}
      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-3">

        <div className="rounded-xl bg-white p-6 shadow">
          <h2 className="font-semibold text-gray-700">
            Normal Roads
          </h2>

          <p className="mt-3 text-2xl font-bold text-green-600">
            12
          </p>
        </div>

        <div className="rounded-xl bg-white p-6 shadow">
          <h2 className="font-semibold text-gray-700">
            Medium Congestion
          </h2>

          <p className="mt-3 text-2xl font-bold text-yellow-600">
            5
          </p>
        </div>

        <div className="rounded-xl bg-white p-6 shadow">
          <h2 className="font-semibold text-gray-700">
            High Congestion
          </h2>

          <p className="mt-3 text-2xl font-bold text-red-600">
            3
          </p>
        </div>

      </div>

      {/* Map Area */}
      <div className="mt-8 rounded-xl bg-white p-6 shadow">

        <h2 className="text-xl font-bold text-gray-800">
          Traffic Map
        </h2>

        <p className="mt-2 text-gray-600">
          Live traffic conditions by road.
        </p>

        {/* Mock Map */}
        <div className="relative mt-6 flex h-96 items-center justify-center overflow-hidden rounded-xl border border-gray-300 bg-gray-200">

          <div className="absolute inset-0 opacity-40">

            <div className="absolute left-1/4 top-0 h-full w-2 rotate-12 bg-gray-500"></div>

            <div className="absolute left-1/2 top-0 h-full w-2 -rotate-12 bg-gray-500"></div>

            <div className="absolute left-0 top-1/2 h-2 w-full rotate-6 bg-gray-500"></div>

            <div className="absolute left-0 top-1/3 h-2 w-full -rotate-6 bg-gray-500"></div>

          </div>

          {/* Road Markers */}

          <div className="absolute left-[25%] top-[35%] h-5 w-5 rounded-full bg-green-500 shadow-lg"></div>

          <div className="absolute left-[50%] top-[50%] h-5 w-5 rounded-full bg-yellow-500 shadow-lg"></div>

          <div className="absolute right-[25%] top-[30%] h-5 w-5 rounded-full bg-red-500 shadow-lg"></div>

          {/* Map Message */}

          <div className="z-10 rounded-lg bg-white px-6 py-4 text-center shadow-lg">

            <p className="font-semibold text-gray-800">
              Live Map Preview
            </p>

            <p className="mt-1 text-sm text-gray-500">
              Traffic data will appear here
            </p>

          </div>

        </div>

        {/* Legend */}
        <div className="mt-6 flex flex-wrap gap-6">

          <div className="flex items-center gap-2">
            <span className="h-4 w-4 rounded-full bg-green-500"></span>

            <span className="text-sm text-gray-600">
              Normal
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="h-4 w-4 rounded-full bg-yellow-500"></span>

            <span className="text-sm text-gray-600">
              Medium
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="h-4 w-4 rounded-full bg-red-500"></span>

            <span className="text-sm text-gray-600">
              High
            </span>
          </div>

        </div>

      </div>

    </main>
  );
}