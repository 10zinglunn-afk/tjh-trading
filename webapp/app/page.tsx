"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  fetchTickers, fetchRun, pct, num,
  type Results, type TickerInfo,
} from "@/lib/api";
import { PriceChart, PositionStrip, EquityChart } from "@/components/Charts";

// strategy id -> walk-forward key in the payload (only tuned strategies have one)
const WF_KEY: Record<string, string> = { meanrev_20_1: "mean_reversion", kronos: "kronos" };

export default function Home() {
  const [tickers, setTickers] = useState<TickerInfo[]>([]);
  const [ticker, setTicker] = useState("synthetic");
  const [strategy, setStrategy] = useState("meanrev_20_1");
  const [spread, setSpread] = useState(3);
  const [slippage, setSlippage] = useState(1);
  const [res, setRes] = useState<Results | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
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
          setRes(r);
          if (!r.strategies[strategy]) setStrategy(Object.keys(r.strategies)[0]);
        })
        .catch((e) => setErr(e.message))
        .finally(() => setLoading(false));
    }, 250);
    return () => clearTimeout(debounce.current);
  }, [ticker, spread, slippage]); // eslint-disable-line react-hooks/exhaustive-deps

  const strat = res?.strategies[strategy];
  const displayRegime = res?.meta.display_regime ?? "custom";
  const wf = res && WF_KEY[strategy] ? res.walk_forward[WF_KEY[strategy]] : undefined;

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
      <header className="header" style={{ marginBottom: 20 }}>
        <h1>The Skeptic&apos;s Machine</h1>
        <p>
          A pretty signal is not a real edge. Pick a strategy, then watch it look good with
          no costs and fall apart once you pay real spreads and test it out-of-sample. Every
          number here is computed by the canonical Python harness — nothing is faked in the browser.
        </p>
      </header>

      {/* Controls */}
      <div className="panel" style={{ marginBottom: 16 }}>
        <div className="controls">
          <div className="field">
            <label>Ticker</label>
            <select value={ticker} onChange={(e) => setTicker(e.target.value)}>
              {tickers.map((t) => (
                <option key={t.id} value={t.id}>{t.label}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Strategy</label>
            <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
              {res &&
                Object.entries(res.strategies).map(([id, s]) => (
                  <option key={id} value={id}>{s.label}</option>
                ))}
            </select>
          </div>
          <div className="field">
            <label>Spread: {spread} bps</label>
            <input type="range" min={0} max={400} step={1} value={spread}
              onChange={(e) => setSpread(Number(e.target.value))} />
          </div>
          <div className="field">
            <label>Slippage: {slippage} bps</label>
            <input type="range" min={0} max={100} step={1} value={slippage}
              onChange={(e) => setSlippage(Number(e.target.value))} />
          </div>
          <div className="field">
            <label>&nbsp;</label>
            <span className="pill">
              {loading ? "running…" : res ? `${res.meta.bars} bars · ${res.meta.start} → ${res.meta.end}` : ""}
            </span>
          </div>
        </div>
        {strat && <p className="muted" style={{ margin: "12px 2px 0" }}>{strat.description}</p>}
      </div>

      {err && <div className="banner warn err" style={{ marginBottom: 16 }}>{err}</div>}

      {res && res.data_quality.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 16 }}>
          {res.data_quality.map((d, i) => (
            <div key={i} className={`banner ${d.level === "warn" ? "warn" : "info"}`}>
              <strong>{d.code}</strong> — {d.message}
            </div>
          ))}
        </div>
      )}

      {strat && res && (
        <>
          {/* Price + signal */}
          <div className="panel grow" style={{ marginBottom: 16 }}>
            <p className="section-title">Price &amp; signal — {strat.label}</p>
            <PriceChart dates={res.prices.dates} close={res.prices.close} strat={strat} />
            <PositionStrip dates={res.prices.dates} positions={strat.positions} />
            <div className="legend" style={{ marginTop: 6 }}>
              <span><span className="swatch" style={{ background: "#5b9dff" }} />Price</span>
              <span><span className="swatch" style={{ background: "#38d39f" }} />Long entry / held long</span>
              <span><span className="swatch" style={{ background: "#ff5d6c" }} />Short entry / held short</span>
            </div>
          </div>

          {/* Equity */}
          <div className="panel" style={{ marginBottom: 16 }}>
            <p className="section-title">
              Growth of $1 — strategy net of costs vs buy &amp; hold (costs: {spread}/{slippage} bps)
            </p>
            <EquityChart
              dates={res.prices.dates}
              stratNet={strat.equity.net}
              stratGross={strat.equity.gross}
              buyHoldNet={res.strategies["buy_and_hold"].equity.net}
            />
            <div className="legend" style={{ marginTop: 6 }}>
              <span><span className="swatch" style={{ background: "#38d39f" }} />Strategy (net of costs)</span>
              <span><span className="swatch" style={{ background: "#ffb454" }} />Buy &amp; hold</span>
              <span><span className="swatch" style={{ background: "#7d8aa3" }} />Strategy (frictionless — the lie)</span>
            </div>
          </div>

          <div className="row">
            {/* Verdict / OOS */}
            <div className="panel grow" style={{ flexBasis: 420 }}>
              <p className="section-title">Out-of-sample verdict (walk-forward)</p>
              {wf ? (
                <>
                  <div className="verdict" style={{ marginBottom: 14 }}>
                    <span className={`tag ${verdict?.survives ? "advance" : "kill"}`}>
                      {verdict?.survives ? "SURVIVES OOS" : "KILL"}
                    </span>
                    <span className="muted">
                      params chosen on train only, scored on unseen test · {wf.params_per_fold.length} folds
                    </span>
                  </div>
                  <div className="metric-grid">
                    <Metric k="OOS return" v={pct(wf.oos_metrics.total_return)} sign={wf.oos_metrics.total_return} />
                    <Metric k="Sharpe" v={num(wf.oos_metrics.sharpe)} sign={wf.oos_metrics.sharpe} />
                    <Metric k="Max DD" v={pct(wf.oos_metrics.max_drawdown)} sign={-1} />
                    <Metric k="Trades" v={String(wf.oos_metrics.num_trades ?? "—")} />
                    <Metric k="Win rate" v={pct(wf.oos_metrics.win_rate)} />
                  </div>
                  <p className="muted" style={{ marginTop: 12, marginBottom: 0 }}>
                    Buy &amp; hold over the same series returned {pct(verdict?.bh)}. The only honest
                    question: does the OOS net-of-cost number beat that? Usually it does not.
                  </p>
                </>
              ) : (
                <p className="muted">
                  No walk-forward for this strategy — it has no tunable parameters
                  (buy&amp;hold and random are baselines, not edges to validate).
                </p>
              )}
            </div>

            {/* Cost regime table */}
            <div className="panel grow" style={{ flexBasis: 420 }}>
              <p className="section-title">What costs do to {strat.label}</p>
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
              <p className="muted" style={{ marginTop: 12, marginBottom: 0 }}>
                Frictionless is the lie. The cheap-option row (300/50 bps) is why naive options
                trading is ruin. Drag the sliders to set your own assumption.
              </p>
            </div>
          </div>
        </>
      )}

      {!res && !err && <p className="spinner" style={{ marginTop: 24 }}>Loading the harness…</p>}

      <footer style={{ marginTop: 40 }} className="muted">
        Source of truth: the Python harness (<code>costs.py</code>, <code>backtest.py</code>,
        <code> walkforward.py</code>). No-lookahead is enforced in the engine
        (<code>positions.shift(1)</code>); the browser only displays what Python computed.
      </footer>
    </div>
  );
}

function Metric({ k, v, sign }: { k: string; v: string; sign?: number | null }) {
  const cls = sign == null ? "" : sign >= 0 ? "good" : "bad";
  return (
    <div className="metric">
      <div className="k">{k}</div>
      <div className={`v ${cls}`}>{v}</div>
    </div>
  );
}
