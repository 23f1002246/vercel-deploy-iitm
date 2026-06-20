import json, statistics
from collections import defaultdict
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST","OPTIONS","GET"],
    allow_headers=["*"],
)

DATA = json.loads((Path(__file__).parent / "telemetry.json").read_text())

def percentile(xs, p):
    if not xs:
        return 0.0
    s = sorted(xs)
    k = (len(s) - 1) * p
    f = int(k); c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)

@app.post("/api")
async def metrics(req: Request):
    body = await req.json()
    regions = body.get("regions", [])
    thr = float(body.get("threshold_ms", 0))
    groups = defaultdict(list)
    for row in DATA:
        if row["region"] in regions:
            groups[row["region"]].append(row)
    out = {}
    for r in regions:
        rows = groups.get(r, [])
        lats = [x["latency_ms"] for x in rows]
        ups  = [x["uptime_pct"] for x in rows]
        out[r] = {
            "avg_latency": round(statistics.fmean(lats), 2) if lats else 0,
            "p95_latency": round(percentile(lats, 0.95), 2) if lats else 0,
            "avg_uptime":  round(statistics.fmean(ups), 3)  if ups  else 0,
            "breaches":    sum(1 for v in lats if v > thr),
        }
    return out
