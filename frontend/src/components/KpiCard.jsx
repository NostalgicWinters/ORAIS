// components/KpiCard.jsx
export default function KpiCard({ label, value }) {
  return (
    <div style={{ background: "#16191f", padding: 20 }}>
      <p>{label}</p>
      <h2>{value}</h2>
    </div>
  );
}