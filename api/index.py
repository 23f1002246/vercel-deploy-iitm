# Vercel Python Serverless Function (native BaseHTTPRequestHandler).
# Vercel auto-routes this file to /api — no vercel.json rewrites needed.
import json
import statistics
from collections import defaultdict
from http.server import BaseHTTPRequestHandler
from pathlib import Path

DATA = json.loads((Path(__file__).parent / "telemetry.json").read_text())


def percentile(xs, p):
    if not xs:
        return 0.0
    s = sorted(xs)
    k = (len(s) - 1) * p
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def compute(body):
    regions = body.get("regions", []) or []
    thr = float(body.get("threshold_ms", 0))
    groups = defaultdict(list)
    for row in DATA:
        if row.get("region") in regions:
            groups[row["region"]].append(row)
    out = []
    for r in regions:
        rows = groups.get(r, [])
        lats = [x["latency_ms"] for x in rows]
        ups  = [x["uptime_pct"] for x in rows]
        out.append({
            "region":      r,
            "avg_latency": round(statistics.fmean(lats), 2) if lats else 0,
            "p95_latency": round(percentile(lats, 0.95), 2) if lats else 0,
            "avg_uptime":  round(statistics.fmean(ups), 3)  if ups  else 0,
            "breaches":    sum(1 for v in lats if v > thr),
        })
    return {"regions": out}


class handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Expose-Headers", "*")
        self.send_header("Access-Control-Max-Age", "86400")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        payload = json.dumps({
            "status": "ok",
            "usage": 'POST JSON {"regions":["apac","amer"],"threshold_ms":180}'
        }).encode()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            body = {}
        result = compute(body)
        payload = json.dumps(result).encode()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
