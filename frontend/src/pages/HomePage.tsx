import { useEffect, useState } from "react";
import { getHealth } from "../services/api";
import type { HealthStatus } from "../types";

function HomePage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then((result) => setHealth(result))
      .catch(() => setError("Unable to reach backend API."));
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-gray-50 px-4 text-center">
      <h1 className="text-3xl font-semibold text-gray-900">CircularCarbon AI</h1>

      {!health && !error && (
        <p className="text-gray-500">Checking backend connection...</p>
      )}

      {health && (
        <p className="rounded-md bg-green-100 px-4 py-2 text-green-800">
          Backend status: {health.status}
        </p>
      )}

      {error && (
        <p className="rounded-md bg-red-100 px-4 py-2 text-red-800">{error}</p>
      )}
    </div>
  );
}

export default HomePage;
