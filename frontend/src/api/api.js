const BASE_URL = "http://localhost:8000";

export async function fetchKPIs() {
  const res = await fetch(`${BASE_URL}/kpis`);
  if (!res.ok) throw new Error("Failed to fetch KPIs");
  return res.json();
}

export async function fetchOverview() {
  const res = await fetch(`${BASE_URL}/overview`);
  if (!res.ok) throw new Error("Failed to fetch overview");
  return res.json();
}