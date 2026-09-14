"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import {
  fetchTickers, fetchRun, pct, num,
  type Results, type TickerInfo, type Diagnostics,
} from "@/lib/api";
import { PriceChart, PositionStrip, EquityChart } from "@/components/Charts";
import { TrackRecord } from "@/components/TrackRecord";

// strategy id -> walk-forward key in the payload (only tuned strategies have one)
const WF_KEY: Record<string, string> = { meanrev_20_1: "mean_reversion", kronos: "kronos" };

// Real data first: SPY is fetched live by the backend (yfinance). If that fails
// (backend asleep, rate-limited), we fall back to the synthetic teaching fixture.
const DEFAULT_TICKER = "spy";

export default function Home() {
  const [tickers, setTickers] = useState<TickerInfo[]>([]);
  const [ticker, setTicker] = useState(DEFAULT_TICKER);
  const [strategy, setStrategy] = useState("meanrev_20_1");
  const [spread, setSpread] = useState(3);
  const [slippage, setSlippage] = useState(1);
  const [res, setRes] = useState<Results | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [fellBack, setFellBack] = useState(false);
  const everLoaded = useRef(false);
  const debounce = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    fetchTickers()
      .then((t) => setTickers(t.tickers))
      .catch((e) => setErr(`Cannot reach the harness API at the configured URL. ${e.message}`));
  }, []);

  useEffect(() => {
    clearTimeout(debounce.current);
    debounce.current = setTimeout(() => {
      setLoading(true);
      setErr(null);
      fetchRun({ ticker, spread_bps: spread, slippage_bps: slippage })
        .then((r) => {
          everLoaded.current = true;
          setRes(r);
          if (!r.strategies[strategy]) setStrategy(Object.keys(r.strategies)[0]);
        })
        .catch((e) => {
          if (!everLoaded.current && ticker === DEFAULT_TICKER) {
            // First load and real data unavailable -> demo fixture instead of an error page.
            setFellBack(true);
            setTicker("synthetic");
          } else {
            setErr(e.message);
          }
        })
        .finally(() => setLoading(false));
    }, 250);
    return () => clearTimeout(debounce.current);
  }, [ticker, spread, slippage]); // eslint-disable-line react-hooks/exhaustive-deps

  const strat = res?.strategies[strategy];
  const displayRegime = res?.meta.display_regime ?? "custom";
  const wf = res && WF_KEY[strategy] ? res.walk_forward[WF_KEY[strategy]] : undefined;
  const isSynthetic = ticker === "synthetic";

  const verdict = useMemo(() => {
    if (!res || !wf?.oos_metrics) return null;
    const oos = wf.oos_metrics.total_return;
    const bh = res.metrics["buy_and_hold"]?.[displayRegime]?.total_return ?? 0;
    if (oos === null) return null;
    const survives = oos > 0 && oos > bh;
    return { oos, bh, survives };
  }, [res, wf, displayRegime]);

  return (
    <div className="container">
      <div className="sm-top">
        <div className="sm-title">The Skeptic&apos;s Machine <span>· visualizer v1</span></div>
        <div className="sm-pickers">
          <span className="sm-pill">Ticker:{" "}
            <select value={ticker} onChange={(e) => setTicker(e.target.value)}>
              {!tickers.some((t) => t.id === ticker) && (
                <option value={ticker}>{ticker.toUpperCase()}</option>
              )}
              {tickers.map((t) => (
                <option key={t.id} value={t.id}>{t.label}</option>
              ))}
            </select>
          </span>
          <span className="sm-pill">Strategy:{" "}
            <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
              {res &&
                Object.entries(res.strategies).map(([id, s]) => (
                  <option key={id} value={id}>{s.label}</option>
                ))}
            </select>
          </span>
          <span className="sm-pill tertiary">
            {loading ? "running…" : res ? `${res.meta.bars} bars · ${res.meta.start} → ${res.meta.end}` : ""}
          </span>
          <span className="sm-pill">
            <Link href="/engine" style={{ textDecoration: "none", fontWeight: 600 }}>
              Engine Room →
            </Link>
          </span>
        </div>
      </div>
      <p className="sm-sub">
        A pretty signal is not a real edge. Pick a strategy, watch it look good with no costs,
        then watch it fall apart once it pays real spreads and is tested out-of-sample. Every
        number is computed by the canonical Python harness — the browser only draws.
      </p>

      {err && <div className="banner warn err" style={{ marginBottom: 12 }}>{err}</div>}

      {isSynthetic && res && (
        <div className="banner warn" style={{ marginBottom: 12 }}>
          <strong>Synthetic teaching fixture</strong> — this series has a mean-reversion edge
          deliberately baked in (it is how we verify the machine can detect a real edge).
          Any &quot;SURVIVES&quot; verdict here is the fixture flattering itself, not research.
          {fellBack && " (Shown because live SPY data was unavailable — the free backend sleeps when idle; retry in ~1 min.)"}
          {" "}The real track record is at the bottom of this page.
        </div>
      )}

      {res && res.data_quality.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 12 }}>
          {res.data_quality.map((d, i) => (
            <div key={i} className={`banner ${d.level === "warn" ? "warn" : ""}`}>
              <strong>{d.code}</strong> — {d.message}
            </div>
          ))}
        </div>
      )}

      {strat && res && (
        <div className="sm-grid">
          <div className="sm-col">
            <div className="sm-card">
              <div className="sm-card-h">① Price + signal — {strat.label}
                <span>▲ long entry · ▼ short entry · strip = held position</span>
              </div>
              <PriceChart dates={res.prices.dates} close={res.prices.close} strat={strat} />
              <PositionStrip dates={res.prices.dates} positions={strat.positions} />
            </div>

            <div className="sm-card">
              <div className="sm-card-h">② Growth of $1, net of costs
                <span>costs: {spread}/{slippage} bps</span>
              </div>
              <EquityChart
                dates={res.prices.dates}
                stratNet={strat.equity.net}
                stratGross={strat.equity.gross}
                buyHoldNet={res.strategies["buy_and_hold"].equity.net}
              />
              <div className="sm-legend">
                <span><i style={{ background: "#d4483b" }} />Strategy, after costs</span>
                <span><i style={{ background: "#2e9e5b" }} />Buy &amp; hold</span>
                <span><i style={{ background: "#9a9a9a" }} />Strategy, frictionless (the lie)</span>
              </div>
            </div>

            <div className="sm-card">
              <div className="sm-card-h">③ Cost assumptions <span>drag → everything recomputes in Python</span></div>
              <div className="sm-slider">
                <label>Spread</label>
                <input type="range" min={0} max={400} step={1} value={spread}
                  onChange={(e) => setSpread(Number(e.target.value))} />
                <span className="val">{spread.toFixed(1)} bps</span>
              </div>
              <div className="sm-slider">
                <label>Slippage</label>
                <input type="range" min={0} max={100} step={1} value={slippage}
                  onChange={(e) => setSlippage(Number(e.target.value))} />
                <span className="val">{slippage.toFixed(1)} bps</span>
              </div>
            </div>

            <div className="sm-card">
              <div className="sm-card-h">What costs do to {strat.label}</div>
              <table>
                <thead>
                  <tr><th>Cost regime</th><th>Return</th><th>Sharpe</th><th>Trades</th></tr>
                </thead>
                <tbody>
                  {Object.entries(res.cost_regimes).map(([rk, rc]) => {
                    const m = res.metrics[strategy][rk];
                    return (
                      <tr key={rk}>
                        <td>{rc.label}</td>
                        <td className={(m?.total_return ?? 0) >= 0 ? "good" : "bad"}>{pct(m?.total_return)}</td>
                        <td>{num(m?.sharpe)}</td>
                        <td>{m?.num_trades ?? "—"}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              <p className="muted" style={{ marginTop: 10, marginBottom: 2, fontSize: 11.5 }}>
                Frictionless is the lie. The cheap-option row (300/50 bps) is why naive options
                trading is ruin.
              </p>
            </div>
          </div>

          <div className="sm-col">
            <div className="sm-card" style={{ display: "flex", flexDirection: "column" }}>
              <div className="sm-card-h">④ Verdict <span>OOS, net of costs</span></div>
              {wf ? (
                <>
                  <div className={`sm-badge ${verdict?.survives ? "sm-live" : "sm-dead"}`}>
                    {verdict?.survives ? "SURVIVES OOS ✓" : "DEAD ✕"}
                  </div>
                  <div className="sm-verdict-sub">
                    {verdict?.survives
                      ? "Beats buy & hold OOS after costs on this series — but see the caveats in the track record before believing it."
                      : "Does not beat buy & hold out-of-sample after costs."}
                    {" "}Params chosen on train only · {wf.params_per_fold.length} folds.
                  </div>
                  <div className="sm-metrics">
                    <MetricRow k="OOS return" v={pct(wf.oos_metrics.total_return)} sign={wf.oos_metrics.total_return} />
                    <MetricRow k="Buy & hold" v={pct(verdict?.bh)} sign={verdict?.bh} />
                    <MetricRow k="Sharpe" v={num(wf.oos_metrics.sharpe)} />
                    <MetricRow k="Max drawdown" v={pct(wf.oos_metrics.max_drawdown)} sign={-1} />
                    <MetricRow k="Trades" v={String(wf.oos_metrics.num_trades ?? "—")} />
                    <MetricRow k="Win rate" v={pct(wf.oos_metrics.win_rate)} />
                  </div>
                </>
              ) : (
                <p className="muted" style={{ margin: 0, fontSize: 12 }}>
                  No walk-forward for this strategy — it has no tunable parameters
                  (buy&amp;hold and random are baselines, not edges to validate).
                </p>
              )}
            </div>

            {wf?.diagnostics && (
              <RobustnessPanel d={wf.diagnostics} />
            )}

            <div className="sm-card">
              <div className="sm-card-h">The one rule</div>
              <p className="muted" style={{ margin: 0, fontSize: 12, lineHeight: 1.5 }}>
                A strategy is only real if it beats buy-and-hold <em>and</em> random,
                out-of-sample, net of costs, on real data. Almost nothing does —
                that&apos;s the point of the machine.
              </p>
            </div>
          </div>
        </div>
      )}

      {!res && !err && <p className="spinner" style={{ marginTop: 24 }}>Waking the harness (free backend sleeps when idle — up to ~1 min)…</p>}

      <TrackRecord />

      <div className="sm-foot">
        Source of truth: the Python harness (<code>costs.py</code>, <code>backtest.py</code>,{" "}
        <code>walkforward.py</code>). No-lookahead is enforced in the engine
        (<code>positions.shift(1)</code>); the browser only displays what Python computed.
      </div>
    </div>
  );
}

function RobustnessPanel({ d }: { d: Diagnostics }) {
  const dsrOk = d.deflated_sharpe != null && d.deflated_sharpe >= 0.95;
  return (
    <div className="sm-card">
      <div className="sm-card-h">⑤ Robustness <span>edge, or best-of-{d.n_trials} luck?</span></div>
      <div style={{ display: "flex", gap: 18, flexWrap: "wrap", fontSize: 12, marginBottom: 10 }}>
        <span className="muted">
          Deflated Sharpe:{" "}
          <b className={dsrOk ? "good" : "bad"}>{num(d.deflated_sharpe)}</b>
          {" "}<span style={{ fontSize: 11 }}>(≥0.95 = not just luck)</span>
        </span>
        <span className="muted">
          Trades/fold: <b className={(d.trades_per_fold ?? 0) >= 30 ? "good" : "bad"}>{num(d.trades_per_fold, 0)}</b>
        </span>
      </div>

      {d.regime_split && (
        <p className="muted" style={{ margin: "0 0 10px", fontSize: 12 }}>
          By this ticker&apos;s regime — up <b className="good">{pct(d.regime_split.up.return)}</b>,{" "}
          down {pct(d.regime_split.down.return)},{" "}
          chop <b className="bad">{pct(d.regime_split.chop.return)}</b>
          {" "}<span style={{ fontSize: 11 }}>(a timing edge that only shows in one regime is fragile)</span>
        </p>
      )}

      {d.per_year.length > 0 && (
        <table>
          <thead>
            <tr><th>Year</th><th>OOS return</th><th>Sharpe</th><th>Bars</th></tr>
          </thead>
          <tbody>
            {d.per_year.map((y) => (
              <tr key={y.period} style={y.period === d.best_year ? { fontWeight: 600 } : undefined}>
                <td>{y.period}{y.period === d.best_year ? " ★" : ""}</td>
                <td className={(y.return ?? 0) >= 0 ? "good" : "bad"}>{pct(y.return)}</td>
                <td>{num(y.sharpe)}</td>
                <td>{y.bars}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {d.best_year_share != null && d.best_year_share > 0.6 && (
        <p className="muted" style={{ margin: "6px 0 0", fontSize: 11.5 }}>
          {(d.best_year_share * 100).toFixed(0)}% of the return came from {d.best_year} — a one-year wonder.
        </p>
      )}

      {d.red_flags.length > 0 ? (
        <div style={{
          marginTop: 10, padding: "8px 10px", borderRadius: 6, fontSize: 11.5,
          background: "rgba(220,38,38,0.08)", border: "1px solid rgba(220,38,38,0.25)",
        }}>
          <b className="bad">Red flag{d.red_flags.length > 1 ? "s" : ""}:</b>{" "}
          {d.red_flags.join(" ")}
        </div>
      ) : (
        <p className="muted" style={{ margin: "10px 0 0", fontSize: 11.5 }}>
          No automated red flag fired — still not a green light. Absence of a flag is not proof of edge.
        </p>
      )}
    </div>
  );
}

function MetricRow({ k, v, sign }: { k: string; v: string; sign?: number | null }) {
  const cls = sign == null ? "" : sign >= 0 ? "pos" : "neg";
  return (
    <div>
      <span>{k}</span>
      <b className={cls}>{v}</b>
    </div>
  );
}
