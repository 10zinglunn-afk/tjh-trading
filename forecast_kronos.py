"""Kronos forecaster -- RUN THIS LOCALLY (needs internet + torch; sandbox can't).

Produces a CAUSAL, walk-forward forecast of the next-bar return for a price CSV and
caches it as a sidecar file the harness reads. Kronos itself never runs inside the
backtest -- it would be slow and, worse, tempt lookahead. We separate concerns:

    forecast_kronos.py  -> expensive, offline, generates realdata/<t>.kronos.csv
    strategies.kronos_signal -> cheap, reads the cache, emits positions in [-1,1]

NO LOOKAHEAD: the forecast stored on row t uses ONLY bars up to and including t to
predict bar t+1. pred_ret[t] = predicted_close[t+1]/close[t] - 1. The backtest engine
then shifts positions by one bar, so a t-decision is earned on t+1's real return.

Kronos is a foundation model (https://github.com/shiyu-coder/Kronos). It is only
"real" if kronos_signal beats buy-and-hold OUT-OF-SAMPLE after costs in run.py.
A 30k-star model gets no special treatment from costs.py.

Usage (from inside a clone of the Kronos repo, or with it on PYTHONPATH):
    pip install -r requirements.txt        # the Kronos repo's requirements
    python forecast_kronos.py realdata/tqqq.csv --device cuda:0
    python forecast_kronos.py realdata/tqqq.csv --device cpu --stride 5   # faster, coarser
    python forecast_kronos.py realdata/tqqq.csv --mock                    # NO model: test plumbing only

Then back in this project:
    python run.py realdata/tqqq.csv        # a 'kronos' row now appears

Frequency-agnostic: the next-timestamp step is inferred from the data's own spacing,
so the same script works for daily, hourly, or 5-min bars (intraday is where Kronos
is strongest -- swapping data is all it takes).
"""
import argparse
import sys
import numpy as np
import pandas as pd


def load_ohlcv(path):
    df = pd.read_csv(path, parse_dates=[0], index_col=0)
    df.columns = [c.lower() for c in df.columns]
    need = {"open", "high", "low", "close"}
    missing = need - set(df.columns)
    if missing:
        sys.exit(f"CSV {path} missing required columns: {sorted(missing)}")
    if "volume" not in df.columns:
        df["volume"] = 0.0
    return df


def infer_step(index):
    """Median spacing between bars -> works for daily/hourly/intraday alike."""
    diffs = pd.Series(index).diff().dropna()
    return diffs.median() if len(diffs) else pd.Timedelta(days=1)


def mock_forecast(df, lookback):
    """Deterministic stand-in so you can test the harness WITHOUT downloading Kronos.
    Naive momentum: predicted next return = mean of the last 5 realized returns.
    This is NOT a model -- it exists purely to exercise the plumbing end-to-end."""
    rets = df["close"].pct_change()
    pred = rets.rolling(5).mean().shift(0)        # uses returns through bar t only
    pred.iloc[:lookback] = np.nan                  # respect the warmup window
    return pred


def kronos_forecast(df, lookback, stride, device, model_name, tok_name,
                    temperature, top_p, sample_count, max_bars):
    """Real Kronos: rolling one-step-ahead forecast. One forward pass per (strided) bar."""
    try:
        from model import Kronos, KronosTokenizer, KronosPredictor
    except Exception as e:
        sys.exit(
            "Could not import Kronos. Run this from a clone of "
            "https://github.com/shiyu-coder/Kronos (or add it to PYTHONPATH), "
            f"after `pip install -r requirements.txt`.\nOriginal error: {e}"
        )

    tokenizer = KronosTokenizer.from_pretrained(tok_name)
    model = Kronos.from_pretrained(model_name)
    predictor = KronosPredictor(model, tokenizer, max_context=lookback, device=device)

    step = infer_step(df.index)
    cols = [c for c in ["open", "high", "low", "close", "volume", "amount"] if c in df.columns]
    pred_close = pd.Series(np.nan, index=df.index, dtype=float)

    n = len(df)
    end = n - 1                                     # last bar has no t+1 to predict
    if max_bars:
        end = min(end, lookback + max_bars)
    ts = pd.Series(df.index)

    for t in range(lookback, end):
        if (t - lookback) % stride != 0:
            continue                               # strided: hold the previous forecast
        x_df = df.iloc[t - lookback:t][cols].reset_index(drop=True)
        x_ts = ts.iloc[t - lookback:t].reset_index(drop=True)
        y_ts = pd.Series([df.index[t] + step])     # the t+1 timestamp
        out = predictor.predict(df=x_df, x_timestamp=x_ts, y_timestamp=y_ts,
                                pred_len=1, T=temperature, top_p=top_p,
                                sample_count=sample_count)
        pred_close.iloc[t] = float(out["close"].iloc[0])
        if (t - lookback) % (stride * 25) == 0:
            print(f"  ... bar {t}/{end}", flush=True)

    pred_ret = pred_close / df["close"] - 1.0
    return pred_ret


def main():
    ap = argparse.ArgumentParser(description="Causal Kronos next-bar forecaster.")
    ap.add_argument("csv", help="price CSV: date,open,high,low,close[,volume]")
    ap.add_argument("--lookback", type=int, default=512, help="context window (Kronos max 512)")
    ap.add_argument("--stride", type=int, default=1, help="forecast every N bars (>1 = faster, coarser)")
    ap.add_argument("--device", default="cpu", help="cpu or cuda:0")
    ap.add_argument("--model", default="NeoQuasar/Kronos-small")
    ap.add_argument("--tokenizer", default="NeoQuasar/Kronos-Tokenizer-base")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--top-p", type=float, default=0.9)
    ap.add_argument("--sample-count", type=int, default=1, help="forecast paths to average")
    ap.add_argument("--max-bars", type=int, default=0, help="cap bars for a quick smoke test (0 = all)")
    ap.add_argument("--mock", action="store_true", help="naive momentum stand-in; NO model download")
    ap.add_argument("--out", default=None, help="output path (default: <csv-stem>.kronos.csv)")
    args = ap.parse_args()

    df = load_ohlcv(args.csv)
    if len(df) <= args.lookback + 2:
        sys.exit(f"Need > lookback+2 bars; have {len(df)}, lookback {args.lookback}.")

    if args.mock:
        print(f"[MOCK] naive momentum forecast on {args.csv} (plumbing test only)")
        pred_ret = mock_forecast(df, args.lookback)
    else:
        print(f"Kronos {args.model} on {args.csv}: {len(df)} bars, "
              f"lookback={args.lookback}, stride={args.stride}, device={args.device}")
        pred_ret = kronos_forecast(
            df, args.lookback, args.stride, args.device, args.model, args.tokenizer,
            args.temperature, args.top_p, args.sample_count, args.max_bars)

    out_path = args.out or (args.csv.rsplit(".", 1)[0] + ".kronos.csv")
    out = pd.DataFrame({"pred_ret": pred_ret})
    out.index.name = "date"
    out.to_csv(out_path)
    n_valid = int(pred_ret.notna().sum())
    print(f"wrote {out_path}  ({n_valid} forecasts, "
          f"mean pred_ret={np.nanmean(pred_ret.values):+.5f})")


if __name__ == "__main__":
    main()
