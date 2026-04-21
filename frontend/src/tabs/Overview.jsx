// tabs/Overview.jsx
import React from "react";
import { ResponsiveContainer, AreaChart, Area } from "recharts";

const data = [
  { month: "Aug", actual: 82400 },
  { month: "Sep", actual: 91200 },
];

export default function Overview() {
  return (
    <div style={{ padding: 20 }}>
      <h2>Overview</h2>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <Area dataKey="actual" stroke="#f5a623" fill="#f5a62333" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}