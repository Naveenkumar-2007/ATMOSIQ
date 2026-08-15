const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";

export async function apiClient<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers || {}),
      },
    });

    if (!res.ok) {
      throw new Error(`API Error [${res.status}]: ${res.statusText}`);
    }

    return await res.json();
  } catch (err) {
    console.warn(`[AtmosIQ API Fetch Warning] (${url}):`, err);
    throw err;
  }
}
