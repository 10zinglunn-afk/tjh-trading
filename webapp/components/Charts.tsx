"use client";

import {
  ComposedChart, LineChart, Line, Area, AreaChart, Scatter,
  XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, CartesianGrid,
} from "recharts";
import type { StrategyResult } from "@/lib/api";

const COL = {
  price: "#5b9dff",
  net: "#38d39f",
  gross: "#7d8aa3",
  bh: "#ffb454",
  good: "#38d39f",
  bad: "#ff5d6c",
  grid: "#222a38",
  axis: "#6b7488",
};

function fmtDate(d: string) {
  return d.slice(0, 7); // YYYY-MM
}

/** Price line with trade-entry markers (green = went long, red = went short). */
export function PriceChart({
  dates, close, strat,
}: {
  dates: string[];
  close: (number | null)[];
  strat: StrategyResult;
}) {
  // Merge trade-entry markers into the SINGLE shared data array (long/short price
  // per bar, else null). Giving Scatter its own data array would make Recharts
  // concatenate its categories onto the x-axis and render the timeline twice.
  const longAt = new Map(strat.trades.filter((t) => t.to > 0).map((t) => [t.date, t.price]));
  const shortAt = new Map(strat.trades.filter((t) => t.to < 0).map((t) => [t.date, t.price]));
  const data = dates.map((d, i) => ({
    date: d, close: close[i],
    longEntry: longAt.get(d) ?? null,
    shortEntry: shortAt.get(d) ?? null,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ComposedChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: 4 }}>
        <CartesianGrid stroke={COL.grid} vertical={false} />
        <XAxis dataKey="date" tickFormatter={fmtDate} minTickGap={48}
          tick={{ fill: COL.axis, fontSize: 11 }} stroke={COL.grid} />
        <YAxis domain={["auto", "auto"]} tick={{ fill: COL.axis, fontSize: 11 }}
          stroke={COL.grid} width={48} />
        <Tooltip
          contentStyle={{ background: "#11161f", border: "1px solid #28303f", borderRadius: 8, fontSize: 12 }}
          labelStyle={{ color: "#8a93a6" }} />
        <Line type="monotone" dataKey="close" stroke={COL.price} dot={false} strokeWidth={1.6}
          name="Price" isAnimationActive={false} />
        <Scatter dataKey="longEntry" fill={COL.good} name="Long entry"
          shape="triangle" isAnimationActive={false} />
        <Scatter dataKey="shortEntry" fill={COL.bad} name="Short entry"
          shape="triangle" isAnimationActive={false} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

/** Thin strip showing the held position over time: green above 0 (long),
 *  red below 0 (short), flat at 0. A single area, two-toned by a gradient at 0. */
export function PositionStrip({
  dates, positions,
}: {
  dates: string[];
  positions: (number | null)[];
}) {
  const data = dates.map((d, i) => ({ date: d, pos: positions[i] ?? 0 }));
  return (
    <ResponsiveContainer width="100%" height={70}>
      <AreaChart data={data} margin={{ top: 4, right: 12, bottom: 0, left: 4 }}>
        <defs>
          <linearGradient id="posfill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={COL.good} stopOpacity={0.7} />
            <stop offset="50%" stopColor={COL.good} stopOpacity={0.05} />
            <stop offset="50%" stopColor={COL.bad} stopOpacity={0.05} />
            <stop offset="100%" stopColor={COL.bad} stopOpacity={0.7} />
          </linearGradient>
        </defs>
        <XAxis dataKey="date" hide />
        <YAxis domain={[-1.1, 1.1]} hide />
        <ReferenceLine y={0} stroke={COL.grid} />
        <Tooltip
          contentStyle={{ background: "#11161f", border: "1px solid #28303f", borderRadius: 8, fontSize: 12 }}
          formatter={(v: number) => [v > 0 ? "long" : v < 0 ? "short" : "flat", "position"]}
          labelStyle={{ color: "#8a93a6" }} />
        <Area type="stepAfter" dataKey="pos" stroke="none" fill="url(#posfill)"
          isAnimationActive={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

/** Equity: strategy net-of-costs vs buy & hold, with the frictionless gross line
 *  to make the cost gap visible. All start at 1.0. */
export function EquityChart({
  dates, stratNet, stratGross, buyHoldNet,
}: {
  dates: string[];
  stratNet: (number | null)[];
  stratGross: (number | null)[];
  buyHoldNet: (number | null)[];
}) {
  const data = dates.map((d, i) => ({
    date: d, net: stratNet[i], gross: stratGross[i], bh: buyHoldNet[i],
  }));
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: 4 }}>
        <CartesianGrid stroke={COL.grid} vertical={false} />
        <XAxis dataKey="date" tickFormatter={fmtDate} minTickGap={48}
          tick={{ fill: COL.axis, fontSize: 11 }} stroke={COL.grid} />
        <YAxis tick={{ fill: COL.axis, fontSize: 11 }} stroke={COL.grid} width={48}
          tickFormatter={(v) => `${v.toFixed(1)}x`} />
        <Tooltip
          contentStyle={{ background: "#11161f", border: "1px solid #28303f", borderRadius: 8, fontSize: 12 }}
          formatter={(v: number) => (v == null ? "—" : `${v.toFixed(3)}x`)}
          labelStyle={{ color: "#8a93a6" }} />
        <ReferenceLine y={1} stroke={COL.grid} />
        <Line type="monotone" dataKey="gross" stroke={COL.gross} dot={false} strokeWidth={1.2}
          strokeDasharray="4 3" name="Strategy (frictionless)" isAnimationActive={false} />
        <Line type="monotone" dataKey="bh" stroke={COL.bh} dot={false} strokeWidth={1.4}
          name="Buy & hold" isAnimationActive={false} />
        <Line type="monotone" dataKey="net" stroke={COL.net} dot={false} strokeWidth={2}
          name="Strategy (net of costs)" isAnimationActive={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
