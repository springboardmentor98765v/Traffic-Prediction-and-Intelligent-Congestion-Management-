export default function AlertsPage() {
  const alerts = [
    {
      title: "Heavy Traffic Detected",
      message: "Heavy congestion detected on Main Road.",
      time: "10 minutes ago",
      level: "High",
    },
    {
      title: "Moderate Congestion",
      message: "Traffic is increasing near Central Junction.",
      time: "25 minutes ago",
      level: "Medium",
    },
    {
      title: "Traffic Normal",
      message: "Traffic flow is normal on Airport Road.",
      time: "40 minutes ago",
      level: "Low",
    },
  ];

  return (
    <main className="min-h-screen bg-gray-100 p-6 md:p-8">
      <h1 className="text-3xl font-bold text-gray-800">
        Traffic Alerts
      </h1>

      <p className="mt-2 text-gray-600">
        View important traffic and congestion alerts
      </p>

      <div className="mt-8 space-y-5">
        {alerts.map((alert, index) => (
          <div
            key={index}
            className="rounded-xl bg-white p-6 shadow"
          >
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <h2
                  className={`text-lg font-bold ${
                    alert.level === "High"
                      ? "text-red-600"
                      : alert.level === "Medium"
                      ? "text-yellow-600"
                      : "text-green-600"
                  }`}
                >
                  {alert.title}
                </h2>

                <p className="mt-2 text-gray-700">
                  {alert.message}
                </p>

                <p className="mt-3 text-sm text-gray-500">
                  {alert.time}
                </p>
              </div>

              <span
                className={`w-fit rounded-full px-4 py-2 text-sm font-semibold ${
                  alert.level === "High"
                    ? "bg-red-100 text-red-700"
                    : alert.level === "Medium"
                    ? "bg-yellow-100 text-yellow-700"
                    : "bg-green-100 text-green-700"
                }`}
              >
                {alert.level}
              </span>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}