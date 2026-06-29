"""HTML template for dashboard.py. Single string with a /*DATA*/ placeholder that
dashboard.py replaces with the results JSON. Vanilla JS + inline SVG charts: no CDN,
no build step, works offline. Kept separate from dashboard.py just for readability."""

HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Skeptic's Machine — backtest dashboard</title>
<style>
  :root{
    --bg:#0f1216; --panel:#161b22; --panel2:#1c2530; --ink:#e6edf3; --mut:#8b949e;
    --line:#30363d; --good:#2ea043; --good2:#1b6e2e; --bad:#da3633; --bad2:#8e2420;
    --warn:#d29922; --accent:#58a6ff; --bh:#c9d1d9;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  header{padding:22px 26px;border-bottom:1px solid var(--line);background:var(--panel)}
  h1{margin:0 0 4px;font-size:20px;letter-spacing:.2px}
  .sub{color:var(--mut);font-size:13px}
  .rule{margin-top:10px;padding:8px 12px;border-left:3px solid var(--accent);
    background:var(--panel2);color:var(--mut);font-size:12.5px;border-radius:0 6px 6px 0}
  .rule b{color:var(--ink)}
  main{padding:22px 26px;max-width:1200px;margin:0 auto}
  h2{font-size:15px;margin:26px 0 10px;font-weight:600}
  h2 .hint{color:var(--mut);font-weight:400;font-size:12px;margin-left:8px}
  table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
  .grid td,.grid th{border:1px solid var(--line);padding:0;text-align:center}
  .grid th{background:var(--panel2);color:var(--mut);font-weight:600;padding:8px 10px;font-size:12px}
  .grid th.tk{text-align:left}
  .cell{padding:8px 6px;cursor:pointer;position:relative;min-width:92px}
  .cell .ret{font-size:13px;font-weight:600}
  .cell .oos{font-size:10.5px;margin-top:2px;opacity:.92}
  .tk{font-weight:600;text-align:left;padding:8px 12px;background:var(--panel);cursor:pointer;white-space:nowrap}
  .tk small{display:block;color:var(--mut);font-weight:400;font-size:11px}
  .g-good{background:var(--good2)} .g-good .ret{color:#7ee787}
  .g-bad{background:var(--bad2)}  .g-bad .ret{color:#ff9d96}
  .g-base{background:var(--panel2)} .g-base .ret{color:var(--bh)}
  .cell:hover{outline:2px solid var(--accent);outline-offset:-2px}
  .legend{margin:10px 0 0;color:var(--mut);font-size:12px;display:flex;gap:18px;flex-wrap:wrap}
  .sw{display:inline-block;width:11px;height:11px;border-radius:2px;vertical-align:-1px;margin-right:5px}
  .badge{display:inline-block;padding:1px 6px;border-radius:10px;font-size:10px;font-weight:600}
  .b-good{background:var(--good2);color:#7ee787}
  .b-bad{background:var(--bad2);color:#ff9d96}
  .b-na{background:var(--panel2);color:var(--mut)}
  #detail{margin-top:8px}
  .panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px;margin-top:14px}
  .panel h3{margin:0 0 2px;font-size:15px}
  .panel .meta{color:var(--mut);font-size:12px;margin-bottom:14px}
  .cols{display:grid;grid-template-columns:1.4fr 1fr;gap:18px}
  @media(max-width:820px){.cols{grid-template-columns:1fr}}
  .chartwrap{background:var(--panel2);border-radius:8px;padding:10px}
  .clegend{font-size:11.5px;color:var(--mut);display:flex;gap:14px;flex-wrap:wrap;margin-top:6px}
  .clegend span{display:flex;align-items:center}
  .ml{display:inline-block;width:16px;height:3px;border-radius:2px;margin-right:5px}
  table.detail{font-size:12.5px;margin-top:4px}
  table.detail th,table.detail td{padding:5px 9px;border-bottom:1px solid var(--line);text-align:right}
  table.detail th:first-child,table.detail td:first-child{text-align:left}
  table.detail th{color:var(--mut);font-weight:600}
  .pos{color:#7ee787}.neg{color:#ff9d96}
  .tag{font-size:11px;color:var(--mut)}
  .foot{color:var(--mut);font-size:11.5px;margin-top:30px;border-top:1px solid var(--line);padding-top:12px}
  .pill{cursor:pointer;border:1px solid var(--line);background:var(--panel2);color:var(--ink);
    border-radius:14px;padding:3px 12px;font-size:12px;margin-right:6px}
  .pill.on{border-color:var(--accent);color:var(--accent)}
</style>
</head>
<body>
<header>
  <h1>The Skeptic's Machine</h1>
  <div class="sub" id="sub"></div>
  <div class="rule">The one rule: a strategy is only <b>real</b> if it beats dumb baselines
  (buy&amp;hold, random) <b>out-of-sample, after realistic costs</b>. Cells are colored vs
  buy-and-hold. The <b>OOS badge</b> is the only number that isn't lying — everything else
  is in-sample and flatters the strategy.</div>
</header>
<main>
  <h2>Survival grid <span class="hint">net return under Liquid-ETF costs (3/1 bps) · click any cell for detail</span></h2>
  <div id="grid"></div>
  <div class="legend">
    <span><i class="sw" style="background:var(--good2)"></i>beats buy&amp;hold</span>
    <span><i class="sw" style="background:var(--bad2)"></i>loses to buy&amp;hold</span>
    <span><i class="sw" style="background:var(--panel2)"></i>baseline</span>
    <span><i class="badge b-good">OOS</i> survives walk-forward</span>
    <span><i class="badge b-bad">OOS</i> fails walk-forward</span>
    <span><i class="badge b-na">—</i> no walk-forward (in-sample only)</span>
  </div>
  <div id="detail"></div>
  <div class="foot">
    Generated by <code>dashboard.py</code> from the canonical harness — numbers match
    <code>run.py</code> exactly. <b>FRICTIONLESS</b> is the lie (raw signal). <b>ETF</b> is
    the truth for stocks. <b>OOS</b> picks params on past data only, scores on unseen data.
    “Nothing beats buy-and-hold” is a valid result, not a failure.
  </div>
</main>
<script>
const DATA = /*DATA*/;
const $ = (s,el=document)=>el.querySelector(s);
const pct = v => v==null||isNaN(v) ? '—' : (v*100).toFixed(1)+'%';
const cls = v => v==null||isNaN(v) ? '' : (v>=0?'pos':'neg');
const NAMES = {buy_and_hold:'Buy & Hold', random:'Random', sma_20_100:'SMA 20/100',
  meanrev_20_1:'Mean-rev z', kronos:'Kronos'};
const nm = k => NAMES[k]||k;

// union of strategies across tickers, stable order
const ORDER = ['buy_and_hold','random','sma_20_100','meanrev_20_1','kronos'];
const allStrats = ORDER.filter(s => DATA.tickers.some(t => t.strategies.includes(s)));

$('#sub').textContent = `${DATA.tickers.length} tickers · generated ${DATA.generated}`;

function survivalClass(t, s){
  if(s==='buy_and_hold') return 'g-base';
  const bh = t.metrics.buy_and_hold?.etf?.total_return;
  const r  = t.metrics[s]?.etf?.total_return;
  if(r==null||bh==null) return '';
  return r>bh ? 'g-good':'g-bad';
}
function oosBadge(t, s){
  const o = t.oos?.[s];
  if(!o) return '<span class="badge b-na">—</span>';
  const bh = t.metrics.buy_and_hold?.etf?.total_return;
  const r = o.metrics.total_return;
  const good = r!=null && bh!=null && r>bh;
  return `<span class="badge ${good?'b-good':'b-bad'}">OOS ${pct(r)}</span>`;
}

function buildGrid(){
  let h = '<table class="grid"><thead><tr><th class="tk">Ticker</th>';
  allStrats.forEach(s => h += `<th>${nm(s)}</th>`);
  h += '</tr></thead><tbody>';
  DATA.tickers.forEach((t,ti)=>{
    h += `<tr><td class="tk" onclick="showDetail(${ti})">${t.ticker.toUpperCase()}
          <small>${t.bars} bars · ${t.start}→${t.end}</small></td>`;
    allStrats.forEach(s=>{
      if(!t.strategies.includes(s)){ h+='<td class="cell g-base"><div class="ret">—</div></td>'; return; }
      const r = t.metrics[s]?.etf?.total_return;
      h += `<td class="cell ${survivalClass(t,s)}" onclick="showDetail(${ti},'${s}')">
              <div class="ret">${pct(r)}</div>
              <div class="oos">${oosBadge(t,s)}</div></td>`;
    });
    h += '</tr>';
  });
  h += '</tbody></table>';
  $('#grid').innerHTML = h;
}

// ---- inline SVG line chart (log-friendly via auto scaling) ----
const PALETTE = {buy_and_hold:'#c9d1d9', random:'#8957e5', sma_20_100:'#58a6ff',
  meanrev_20_1:'#d29922', kronos:'#f778ba', oos:'#2ea043'};
function lineChart(series, opts={}){
  // series: [{name,color,points:[[date,val]...],dash}]
  const W=560,H=300,P={l:48,r:12,t:12,b:28};
  let lo=Infinity,hi=-Infinity,n=0;
  series.forEach(s=>s.points.forEach(p=>{lo=Math.min(lo,p[1]);hi=Math.max(hi,p[1]);n=Math.max(n,s.points.length)}));
  if(!isFinite(lo)){return '<div class="tag">no data</div>';}
  if(lo===hi){hi=lo+1;}
  const pad=(hi-lo)*0.06; lo-=pad; hi+=pad;
  const x=i=>P.l+(i/(n-1||1))*(W-P.l-P.r);
  const y=v=>P.t+(1-(v-lo)/(hi-lo))*(H-P.t-P.b);
  let svg=`<svg viewBox="0 0 ${W} ${H}" width="100%" preserveAspectRatio="xMidYMid meet">`;
  // gridlines + y labels
  for(let g=0;g<=4;g++){
    const v=lo+(hi-lo)*g/4, yy=y(v);
    svg+=`<line x1="${P.l}" y1="${yy}" x2="${W-P.r}" y2="${yy}" stroke="#30363d" stroke-width="1"/>`;
    svg+=`<text x="${P.l-6}" y="${yy+3}" fill="#8b949e" font-size="10" text-anchor="end">${(v).toFixed(1)}x</text>`;
  }
  // baseline at equity=1
  if(lo<1&&hi>1){const y1=y(1);svg+=`<line x1="${P.l}" y1="${y1}" x2="${W-P.r}" y2="${y1}" stroke="#6e7681" stroke-dasharray="2 3"/>`;}
  series.forEach(s=>{
    if(!s.points.length) return;
    const d=s.points.map((p,i)=>(i?'L':'M')+x(i).toFixed(1)+' '+y(p[1]).toFixed(1)).join(' ');
    svg+=`<path d="${d}" fill="none" stroke="${s.color}" stroke-width="${s.name==='Buy & Hold'?2.4:1.6}"
           ${s.dash?'stroke-dasharray="5 4"':''} opacity="0.95"/>`;
  });
  // x end labels
  const first=series.find(s=>s.points.length);
  if(first){
    svg+=`<text x="${P.l}" y="${H-8}" fill="#8b949e" font-size="10">${first.points[0][0]}</text>`;
    svg+=`<text x="${W-P.r}" y="${H-8}" fill="#8b949e" font-size="10" text-anchor="end">${first.points[first.points.length-1][0]}</text>`;
  }
  svg+='</svg>';
  return svg;
}

function showDetail(ti, focus){
  const t = DATA.tickers[ti];
  // equity curves: all strategies (ETF regime) + OOS curves
  const series = t.strategies.map(s=>({
    name:nm(s), color:PALETTE[s]||'#888', points:t.curves[s]||[]
  }));
  Object.keys(t.oos||{}).forEach(s=>{
    const o=t.oos[s];
    if(o.curve&&o.curve.length) series.push({name:nm(s)+' (OOS)',color:PALETTE.oos,points:o.curve,dash:true});
  });
  let leg = series.map(s=>`<span><i class="ml" style="background:${s.color};${s.dash?'background-image:repeating-linear-gradient(90deg,'+s.color+' 0 5px,transparent 5px 9px)':''}"></i>${s.name}</span>`).join('');

  // cost-regime table
  let rt = '<table class="detail"><thead><tr><th>Strategy</th>';
  DATA.regimes.forEach(r=>rt+=`<th>${r.label}</th>`);
  rt+='<th>OOS (net, ETF)</th></tr></thead><tbody>';
  t.strategies.forEach(s=>{
    rt+=`<tr><td>${nm(s)}</td>`;
    DATA.regimes.forEach(r=>{
      const v=t.metrics[s]?.[r.key]?.total_return;
      rt+=`<td class="${cls(v)}">${pct(v)}</td>`;
    });
    const o=t.oos?.[s];
    rt+=`<td class="${o?cls(o.metrics.total_return):''}">${o?pct(o.metrics.total_return):'—'}</td></tr>`;
  });
  rt+='</tbody></table>';

  // risk table (ETF regime sharpe / maxDD / trades)
  let kt='<table class="detail"><thead><tr><th>Strategy</th><th>Sharpe</th><th>Max DD</th><th>Trades</th><th>Win%</th></tr></thead><tbody>';
  t.strategies.forEach(s=>{
    const m=t.metrics[s]?.etf||{};
    kt+=`<tr><td>${nm(s)}</td><td>${m.sharpe==null?'—':m.sharpe.toFixed(2)}</td>
      <td class="neg">${pct(m.max_drawdown)}</td><td>${m.num_trades??'—'}</td>
      <td>${pct(m.win_rate)}</td></tr>`;
  });
  kt+='</tbody></table>';

  $('#detail').innerHTML = `
    <div class="panel">
      <h3>${t.ticker.toUpperCase()} ${focus?'· '+nm(focus):''}</h3>
      <div class="meta">${t.bars} bars · ${t.start} → ${t.end}${t.has_kronos?' · Kronos forecast loaded':''}</div>
      <div class="cols">
        <div>
          <div class="chartwrap">${lineChart(series)}</div>
          <div class="clegend">${leg}</div>
          <div class="tag" style="margin-top:6px">Equity (growth of $1) under ETF costs. Dashed green = out-of-sample walk-forward.</div>
        </div>
        <div>
          <div class="tag">Return by cost regime</div>
          ${rt}
          <div class="tag" style="margin-top:12px">Risk (ETF regime)</div>
          ${kt}
        </div>
      </div>
    </div>`;
  $('#detail').scrollIntoView({behavior:'smooth',block:'nearest'});
}

buildGrid();
showDetail(0);
</script>
</body>
</html>
"""
