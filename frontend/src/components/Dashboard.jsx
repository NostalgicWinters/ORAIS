import { useState, useEffect, useRef } from "react";
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";

// ─── Palette & Theme ────────────────────────────────────────────────────────
// Aesthetic: Industrial data terminal — dark slate + amber signal + cool cyan
// Fonts: "Syne" (headers) + "DM Mono" (data/numbers)

const COLORS = {
  bg: "#0a0c10",
  surface: "#111318",
  card: "#16191f",
  border: "#1e2229",
  amber: "#f5a623",
  amberDim: "#a36b12",
  cyan: "#00d4c8",
  cyanDim: "#007f7a",
  red: "#ff4d6a",
  green: "#00e08a",
  text: "#e8eaf0",
  muted: "#5a6070",
  subtle: "#2a2f3a",
};

// ─── Mock Data ───────────────────────────────────────────────────────────────
const salesData = [
  { month: "Aug", actual: 82400, forecast: 80000, orders: 1240 },
  { month: "Sep", actual: 91200, forecast: 88000, orders: 1380 },
  { month: "Oct", actual: 104500, forecast: 98000, orders: 1590 },
  { month: "Nov", actual: 138700, forecast: 130000, orders: 2100 },
  { month: "Dec", actual: 195000, forecast: 185000, orders: 2960 },
  { month: "Jan", actual: 87300, forecast: 90000, orders: 1320 },
  { month: "Feb", actual: null, forecast: 94500, orders: null },
  { month: "Mar", actual: null, forecast: 101200, orders: null },
];

const stockData = [
  { category: "Electronics", stock: 2840, reorder: 500, overstock: 300 },
  { category: "Apparel", stock: 6120, reorder: 1200, overstock: 800 },
  { category: "Home & Garden", stock: 3450, reorder: 700, overstock: 200 },
  { category: "Sports", stock: 1890, reorder: 400, overstock: 150 },
  { category: "Beauty", stock: 4230, reorder: 900, overstock: 400 },
  { category: "Toys", stock: 2100, reorder: 600, overstock: 500 },
];

const topProducts = [
  { id: "SKU-4821", name: "Wireless Headphones Pro", category: "Electronics", stock: 234, demand: 89, trend: "+12%", status: "optimal" },
  { id: "SKU-2930", name: "Running Shoes X500", category: "Sports", stock: 48, demand: 71, trend: "+8%", status: "low" },
  { id: "SKU-7741", name: "Smart Watch Series 3", category: "Electronics", stock: 612, demand: 34, trend: "-3%", status: "excess" },
  { id: "SKU-1104", name: "Yoga Mat Premium", category: "Sports", stock: 19, demand: 90, trend: "+24%", status: "critical" },
  { id: "SKU-5532", name: "Coffee Maker Deluxe", category: "Home & Garden", stock: 143, demand: 58, trend: "+5%", status: "optimal" },
  { id: "SKU-8823", name: "Skincare Set Glow", category: "Beauty", stock: 380, demand: 22, trend: "-8%", status: "excess" },
];

const recentOrders = [
  { id: "#ORD-98234", customer: "Priya Mehta", amount: 284.50, items: 3, status: "shipped", time: "2m ago" },
  { id: "#ORD-98233", customer: "Carlos Vega", amount: 1249.00, items: 1, status: "processing", time: "14m ago" },
  { id: "#ORD-98232", customer: "Aiko Tanaka", amount: 67.90, items: 5, status: "delivered", time: "31m ago" },
  { id: "#ORD-98231", customer: "Marcus Webb", amount: 432.00, items: 2, status: "shipped", time: "1h ago" },
  { id: "#ORD-98230", customer: "Sophie Laurent", amount: 89.99, items: 4, status: "delivered", time: "2h ago" },
];

const suppliers = [
  { name: "TechSource Global", rating: 4.8, onTime: "97%", pending: 3, value: "$84,200" },
  { name: "FastFab Apparel", rating: 4.2, onTime: "91%", pending: 7, value: "$42,800" },
  { name: "HomeGoods Direct", rating: 4.6, onTime: "95%", pending: 2, value: "$28,100" },
  { name: "SportZone Supply", rating: 3.9, onTime: "88%", pending: 5, value: "$19,400" },
];

// ─── Utilities ────────────────────────────────────────────────────────────────
const fmt = (n) => n >= 1000 ? `$${(n / 1000).toFixed(0)}K` : `$${n}`;
const statusColor = (s) => ({ optimal: COLORS.green, low: COLORS.amber, excess: COLORS.cyan, critical: COLORS.red }[s] || COLORS.muted);
const orderColor = (s) => ({ shipped: COLORS.amber, processing: COLORS.cyan, delivered: COLORS.green }[s] || COLORS.muted);

// ─── Components ───────────────────────────────────────────────────────────────
const KpiCard = ({ label, value, sub, accent, delta }) => (
  <div style={{
    background: COLORS.card,
    border: `1px solid ${COLORS.border}`,
    borderTop: `2px solid ${accent}`,
    padding: "20px 24px",
    borderRadius: "4px",
    position: "relative",
    overflow: "hidden",
  }}>
    <div style={{ position: "absolute", top: 0, right: 0, width: 60, height: 60,
      background: `radial-gradient(circle at top right, ${accent}18, transparent 70%)` }} />
    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: COLORS.muted, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 8 }}>{label}</div>
    <div style={{ fontFamily: "'Syne', sans-serif", fontSize: 28, fontWeight: 700, color: COLORS.text, lineHeight: 1 }}>{value}</div>
    <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 8 }}>
      {delta && <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: delta.startsWith("+") ? COLORS.green : COLORS.red, background: delta.startsWith("+") ? `${COLORS.green}18` : `${COLORS.red}18`, padding: "2px 6px", borderRadius: 2 }}>{delta}</span>}
      <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: COLORS.muted }}>{sub}</span>
    </div>
  </div>
);

const SectionTitle = ({ children, accent = COLORS.amber }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
    <div style={{ width: 3, height: 18, background: accent, borderRadius: 2 }} />
    <span style={{ fontFamily: "'Syne', sans-serif", fontSize: 13, fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase", color: COLORS.text }}>{children}</span>
  </div>
);

const Badge = ({ children, color }) => (
  <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color, background: `${color}20`, border: `1px solid ${color}40`, padding: "2px 8px", borderRadius: 2, textTransform: "uppercase", letterSpacing: "0.06em" }}>{children}</span>
);

const StockBar = ({ value, max, color }) => (
  <div style={{ height: 4, background: COLORS.subtle, borderRadius: 2, overflow: "hidden", flex: 1 }}>
    <div style={{ height: "100%", width: `${Math.min(100, (value / max) * 100)}%`, background: color, borderRadius: 2, transition: "width 0.6s ease" }} />
  </div>
);

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: COLORS.card, border: `1px solid ${COLORS.border}`, padding: "10px 14px", borderRadius: 4 }}>
      <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: COLORS.muted, marginBottom: 6 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: p.color || COLORS.text, marginBottom: 2 }}>
          {p.name}: {typeof p.value === "number" ? (p.name?.toLowerCase().includes("revenue") || p.name?.toLowerCase().includes("actual") || p.name?.toLowerCase().includes("forecast") ? `$${p.value.toLocaleString()}` : p.value.toLocaleString()) : "—"}
        </div>
      ))}
    </div>
  );
};

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [activeNav, setActiveNav] = useState("overview");
  const [time, setTime] = useState(new Date());
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    const t = setInterval(() => { setTime(new Date()); setPulse(p => !p); }, 1000);
    return () => clearInterval(t);
  }, []);

  const navItems = [
    { id: "overview", label: "Overview" },
    { id: "inventory", label: "Inventory" },
    { id: "orders", label: "Orders" },
    { id: "suppliers", label: "Suppliers" },
  ];

  const [kpis, setKpis] = useState([]);
  const [overview, setOverview] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [kpiData, overviewData] = await Promise.all([
          fetchKPIs(),
          fetchOverview()
        ]);

        setKpis(kpiData);
        setOverview(overviewData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  if (loading) return <div className="text-center p-10">Loading...</div>;

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: ${COLORS.bg}; color: ${COLORS.text}; font-family: 'DM Mono', monospace; }
        ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: ${COLORS.bg}; } ::-webkit-scrollbar-thumb { background: ${COLORS.subtle}; border-radius: 4px; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes scanline { 0% { transform: translateY(-100%); } 100% { transform: translateY(100vh); } }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.2; } }
        .card-anim { animation: fadeIn 0.4s ease both; }
      `}</style>

      {/* Scanline overlay */}
      <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, pointerEvents: "none", zIndex: 9999,
        background: "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)" }} />

      <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>

        {/* ── Top bar ── */}
        <header style={{ background: COLORS.surface, borderBottom: `1px solid ${COLORS.border}`, padding: "0 28px", display: "flex", alignItems: "center", justifyContent: "space-between", height: 52, position: "sticky", top: 0, zIndex: 100 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ width: 20, height: 20, background: COLORS.amber, clipPath: "polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)", flexShrink: 0 }} />
              <span style={{ fontFamily: "'Syne', sans-serif", fontSize: 14, fontWeight: 800, letterSpacing: "0.06em", color: COLORS.text }}>ORAIS</span>
              <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: COLORS.muted, letterSpacing: "0.1em" }}>/ RETAIL INTELLIGENCE</span>
            </div>
          </div>

          <nav style={{ display: "flex", gap: 2 }}>
            {navItems.map(n => (
              <button key={n.id} onClick={() => setActiveNav(n.id)} style={{
                background: activeNav === n.id ? `${COLORS.amber}18` : "transparent",
                border: `1px solid ${activeNav === n.id ? COLORS.amber : "transparent"}`,
                color: activeNav === n.id ? COLORS.amber : COLORS.muted,
                padding: "5px 14px", borderRadius: 3, cursor: "pointer",
                fontFamily: "'DM Mono', monospace", fontSize: 11, letterSpacing: "0.08em",
                textTransform: "uppercase", transition: "all 0.15s",
              }}>{n.label}</button>
            ))}
          </nav>

          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: COLORS.green, animation: "blink 2s ease infinite" }} />
              <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: COLORS.muted }}>LIVE</span>
            </div>
            <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: COLORS.muted }}>
              {time.toLocaleTimeString("en-US", { hour12: false })}
            </div>
          </div>
        </header>

        <main style={{ flex: 1, padding: "24px 28px", maxWidth: 1400, margin: "0 auto", width: "100%" }}>

          {/* ── Overview Tab ── */}
          {activeNav === "overview" && (
            <div style={{ animation: "fadeIn 0.35s ease" }}>

              {/* KPI Row */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
                <KpiCard label="Revenue / Month" value="$195K" sub="Dec 2024" delta="+40.4%" accent={COLORS.amber} />
                <KpiCard label="Active Orders" value="2,960" sub="this month" delta="+41.0%" accent={COLORS.cyan} />
                <KpiCard label="Forecast (Feb)" value="$94.5K" sub="ML prediction" accent={COLORS.green} />
                <KpiCard label="Stock Alerts" value="4" sub="items need action" accent={COLORS.red} />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1.6fr 1fr", gap: 16, marginBottom: 16 }}>

                {/* Sales + Forecast Chart */}
                <div style={{ background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 4, padding: "20px 20px 12px" }}>
                  <SectionTitle accent={COLORS.amber}>Revenue vs. Forecast</SectionTitle>
                  <ResponsiveContainer width="100%" height={220}>
                    <AreaChart data={salesData} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
                      <defs>
                        <linearGradient id="gActual" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={COLORS.amber} stopOpacity={0.25} />
                          <stop offset="95%" stopColor={COLORS.amber} stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="gForecast" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={COLORS.cyan} stopOpacity={0.15} />
                          <stop offset="95%" stopColor={COLORS.cyan} stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke={COLORS.subtle} />
                      <XAxis dataKey="month" tick={{ fontFamily: "'DM Mono'", fontSize: 10, fill: COLORS.muted }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontFamily: "'DM Mono'", fontSize: 10, fill: COLORS.muted }} axisLine={false} tickLine={false} tickFormatter={v => `$${(v/1000).toFixed(0)}K`} />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend wrapperStyle={{ fontFamily: "'DM Mono'", fontSize: 10, color: COLORS.muted }} />
                      <Area type="monotone" dataKey="actual" name="Actual" stroke={COLORS.amber} strokeWidth={2} fill="url(#gActual)" dot={{ r: 3, fill: COLORS.amber }} connectNulls={false} />
                      <Area type="monotone" dataKey="forecast" name="Forecast" stroke={COLORS.cyan} strokeWidth={2} strokeDasharray="5 3" fill="url(#gForecast)" dot={false} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>

                {/* Recent Orders */}
                <div style={{ background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 4, padding: "20px" }}>
                  <SectionTitle accent={COLORS.cyan}>Recent Orders</SectionTitle>
                  <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    {recentOrders.map(o => (
                      <div key={o.id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 10px", background: COLORS.surface, borderRadius: 3, borderLeft: `2px solid ${orderColor(o.status)}` }}>
                        <div>
                          <div style={{ fontFamily: "'DM Mono'", fontSize: 11, color: COLORS.amber }}>{o.id}</div>
                          <div style={{ fontFamily: "'DM Mono'", fontSize: 10, color: COLORS.muted, marginTop: 2 }}>{o.customer} · {o.items} items</div>
                        </div>
                        <div style={{ textAlign: "right" }}>
                          <div style={{ fontFamily: "'Syne'", fontSize: 13, fontWeight: 700, color: COLORS.text }}>${o.amount.toFixed(2)}</div>
                          <div style={{ display: "flex", gap: 4, justifyContent: "flex-end", marginTop: 3, alignItems: "center" }}>
                            <Badge color={orderColor(o.status)}>{o.status}</Badge>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Stock by category + Order volume */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                <div style={{ background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 4, padding: "20px" }}>
                  <SectionTitle accent={COLORS.green}>Stock by Category</SectionTitle>
                  <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={stockData} barSize={14} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke={COLORS.subtle} vertical={false} />
                      <XAxis dataKey="category" tick={{ fontFamily: "'DM Mono'", fontSize: 9, fill: COLORS.muted }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontFamily: "'DM Mono'", fontSize: 9, fill: COLORS.muted }} axisLine={false} tickLine={false} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="stock" name="Stock" fill={COLORS.cyan} radius={[2, 2, 0, 0]} />
                      <Bar dataKey="reorder" name="Reorder Pt." fill={COLORS.amberDim} radius={[2, 2, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div style={{ background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 4, padding: "20px" }}>
                  <SectionTitle accent={COLORS.amber}>Order Volume Trend</SectionTitle>
                  <ResponsiveContainer width="100%" height={180}>
                    <LineChart data={salesData} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke={COLORS.subtle} />
                      <XAxis dataKey="month" tick={{ fontFamily: "'DM Mono'", fontSize: 10, fill: COLORS.muted }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontFamily: "'DM Mono'", fontSize: 10, fill: COLORS.muted }} axisLine={false} tickLine={false} />
                      <Tooltip content={<CustomTooltip />} />
                      <Line type="monotone" dataKey="orders" name="Orders" stroke={COLORS.amber} strokeWidth={2} dot={{ r: 3, fill: COLORS.amber }} connectNulls={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {/* ── Inventory Tab ── */}
          {activeNav === "inventory" && (
            <div style={{ animation: "fadeIn 0.35s ease" }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
                <KpiCard label="Total SKUs" value="14,820" sub="active products" delta="+2.3%" accent={COLORS.cyan} />
                <KpiCard label="Low Stock" value="3" sub="below reorder pt." accent={COLORS.red} />
                <KpiCard label="Overstock Risk" value="2" sub="excess inventory" accent={COLORS.amber} />
                <KpiCard label="Turnover Rate" value="6.4×" sub="avg annual" delta="+0.8×" accent={COLORS.green} />
              </div>

              <div style={{ background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 4, padding: "20px", marginBottom: 16 }}>
                <SectionTitle accent={COLORS.amber}>Product Inventory Status</SectionTitle>
                <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr 1fr 1fr 1fr", gap: 0, marginBottom: 8 }}>
                  {["Product", "SKU", "Category", "Stock", "Demand Score", "Status"].map(h => (
                    <div key={h} style={{ fontFamily: "'DM Mono'", fontSize: 10, color: COLORS.muted, padding: "6px 12px", textTransform: "uppercase", letterSpacing: "0.08em", borderBottom: `1px solid ${COLORS.border}` }}>{h}</div>
                  ))}
                </div>
                {topProducts.map((p, i) => (
                  <div key={p.id} style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr 1fr 1fr 1fr", alignItems: "center",
                    background: i % 2 === 0 ? "transparent" : `${COLORS.surface}80`,
                    borderBottom: `1px solid ${COLORS.border}20`, transition: "background 0.15s" }}>
                    <div style={{ padding: "10px 12px", fontFamily: "'Syne'", fontSize: 12, fontWeight: 600, color: COLORS.text }}>{p.name}</div>
                    <div style={{ padding: "10px 12px", fontFamily: "'DM Mono'", fontSize: 11, color: COLORS.amber }}>{p.id}</div>
                    <div style={{ padding: "10px 12px", fontFamily: "'DM Mono'", fontSize: 11, color: COLORS.muted }}>{p.category}</div>
                    <div style={{ padding: "10px 12px", display: "flex", flexDirection: "column", gap: 4 }}>
                      <span style={{ fontFamily: "'DM Mono'", fontSize: 12, color: COLORS.text }}>{p.stock}</span>
                      <StockBar value={p.stock} max={700} color={statusColor(p.status)} />
                    </div>
                    <div style={{ padding: "10px 12px", display: "flex", flexDirection: "column", gap: 4 }}>
                      <div style={{ display: "flex", justifyContent: "space-between" }}>
                        <span style={{ fontFamily: "'DM Mono'", fontSize: 11, color: COLORS.text }}>{p.demand}/100</span>
                        <span style={{ fontFamily: "'DM Mono'", fontSize: 10, color: p.trend.startsWith("+") ? COLORS.green : COLORS.red }}>{p.trend}</span>
                      </div>
                      <StockBar value={p.demand} max={100} color={COLORS.cyan} />
                    </div>
                    <div style={{ padding: "10px 12px" }}><Badge color={statusColor(p.status)}>{p.status}</Badge></div>
                  </div>
                ))}
              </div>

              <div style={{ background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 4, padding: "20px" }}>
                <SectionTitle accent={COLORS.cyan}>Reorder Point Analysis</SectionTitle>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={stockData} barSize={18} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={COLORS.subtle} vertical={false} />
                    <XAxis dataKey="category" tick={{ fontFamily: "'DM Mono'", fontSize: 10, fill: COLORS.muted }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontFamily: "'DM Mono'", fontSize: 10, fill: COLORS.muted }} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ fontFamily: "'DM Mono'", fontSize: 10 }} />
                    <Bar dataKey="stock" name="Current Stock" fill={COLORS.cyan} radius={[2,2,0,0]} />
                    <Bar dataKey="reorder" name="Reorder Point" fill={COLORS.red} radius={[2,2,0,0]} opacity={0.7} />
                    <Bar dataKey="overstock" name="Overstock Risk" fill={COLORS.amber} radius={[2,2,0,0]} opacity={0.6} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* ── Orders Tab ── */}
          {activeNav === "orders" && (
            <div style={{ animation: "fadeIn 0.35s ease" }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
                <KpiCard label="Today's Orders" value="147" sub="as of now" delta="+12%" accent={COLORS.amber} />
                <KpiCard label="Processing" value="34" sub="in queue" accent={COLORS.cyan} />
                <KpiCard label="Shipped" value="89" sub="in transit" accent={COLORS.green} />
                <KpiCard label="Avg. Order Value" value="$284" sub="last 30 days" delta="+6.2%" accent={COLORS.green} />
              </div>

              <div style={{ background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 4, padding: "20px" }}>
                <SectionTitle accent={COLORS.amber}>Order Feed</SectionTitle>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr 0.8fr 0.8fr 1fr", gap: 0, marginBottom: 8 }}>
                  {["Order ID", "Customer", "Amount", "Items", "Status"].map(h => (
                    <div key={h} style={{ fontFamily: "'DM Mono'", fontSize: 10, color: COLORS.muted, padding: "6px 12px", textTransform: "uppercase", letterSpacing: "0.08em", borderBottom: `1px solid ${COLORS.border}` }}>{h}</div>
                  ))}
                </div>
                {[...recentOrders, ...recentOrders].map((o, i) => (
                  <div key={`${o.id}-${i}`} style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr 0.8fr 0.8fr 1fr", alignItems: "center",
                    background: i % 2 === 0 ? "transparent" : `${COLORS.surface}80`,
                    borderBottom: `1px solid ${COLORS.border}20` }}>
                    <div style={{ padding: "10px 12px", fontFamily: "'DM Mono'", fontSize: 11, color: COLORS.amber }}>{o.id}</div>
                    <div style={{ padding: "10px 12px", fontFamily: "'Syne'", fontSize: 12, fontWeight: 600, color: COLORS.text }}>{o.customer}</div>
                    <div style={{ padding: "10px 12px", fontFamily: "'DM Mono'", fontSize: 12, color: COLORS.text }}>${o.amount.toFixed(2)}</div>
                    <div style={{ padding: "10px 12px", fontFamily: "'DM Mono'", fontSize: 12, color: COLORS.muted }}>{o.items}</div>
                    <div style={{ padding: "10px 12px", display: "flex", alignItems: "center", gap: 8 }}>
                      <Badge color={orderColor(o.status)}>{o.status}</Badge>
                      <span style={{ fontFamily: "'DM Mono'", fontSize: 10, color: COLORS.muted }}>{o.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── Suppliers Tab ── */}
          {activeNav === "suppliers" && (
            <div style={{ animation: "fadeIn 0.35s ease" }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
                <KpiCard label="Active Suppliers" value="18" sub="global partners" accent={COLORS.cyan} />
                <KpiCard label="Pending POs" value="17" sub="orders outstanding" accent={COLORS.amber} />
                <KpiCard label="Avg. On-Time" value="92.7%" sub="delivery rate" delta="+1.2%" accent={COLORS.green} />
                <KpiCard label="PO Value" value="$174K" sub="total outstanding" accent={COLORS.amber} />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16 }}>
                {suppliers.map((s, i) => (
                  <div key={s.name} style={{ background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 4, padding: "20px", animation: `fadeIn 0.3s ease ${i * 0.07}s both` }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
                      <div>
                        <div style={{ fontFamily: "'Syne'", fontSize: 15, fontWeight: 700, color: COLORS.text }}>{s.name}</div>
                        <div style={{ fontFamily: "'DM Mono'", fontSize: 10, color: COLORS.muted, marginTop: 2 }}>{s.pending} pending orders · {s.value}</div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontFamily: "'Syne'", fontSize: 18, fontWeight: 800, color: COLORS.amber }}>{s.rating}</div>
                        <div style={{ fontFamily: "'DM Mono'", fontSize: 9, color: COLORS.muted }}>RATING</div>
                      </div>
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
                        <span style={{ fontFamily: "'DM Mono'", fontSize: 10, color: COLORS.muted, textTransform: "uppercase" }}>On-time delivery</span>
                        <span style={{ fontFamily: "'DM Mono'", fontSize: 11, color: COLORS.text }}>{s.onTime}</span>
                      </div>
                      <div style={{ height: 4, background: COLORS.subtle, borderRadius: 2 }}>
                        <div style={{ height: "100%", width: s.onTime, background: parseFloat(s.onTime) > 93 ? COLORS.green : COLORS.amber, borderRadius: 2 }} />
                      </div>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, marginTop: 4 }}>
                        <span style={{ fontFamily: "'DM Mono'", fontSize: 10, color: COLORS.muted, textTransform: "uppercase" }}>Supplier rating</span>
                        <span style={{ fontFamily: "'DM Mono'", fontSize: 11, color: COLORS.text }}>{s.rating} / 5.0</span>
                      </div>
                      <div style={{ height: 4, background: COLORS.subtle, borderRadius: 2 }}>
                        <div style={{ height: "100%", width: `${(s.rating / 5) * 100}%`, background: s.rating >= 4.5 ? COLORS.green : s.rating >= 4 ? COLORS.amber : COLORS.red, borderRadius: 2 }} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer style={{ borderTop: `1px solid ${COLORS.border}`, padding: "10px 28px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontFamily: "'DM Mono'", fontSize: 10, color: COLORS.muted }}>ORAIS v2.4.1 · Kaggle Retail Dataset Integration Active</span>
          <div style={{ display: "flex", gap: 16 }}>
            <span style={{ fontFamily: "'DM Mono'", fontSize: 10, color: COLORS.green }}>● MODEL ONLINE</span>
            <span style={{ fontFamily: "'DM Mono'", fontSize: 10, color: COLORS.muted }}>FORECAST CONFIDENCE: 94.2%</span>
          </div>
        </footer>
      </div>
    </>
  );
}