# Q25 — Vercel POST analytics endpoint (native Python handler)

## Why this version
The previous FastAPI version returned 404 on /api because Vercel's path
forwarding didn't line up with FastAPI's routing, and FastAPI's own 404
doesn't get CORS headers from CORSMiddleware. This version uses Vercel's
native Python serverless handler (BaseHTTPRequestHandler subclass named
`handler`) which:
  * Vercel auto-routes api/index.py to /api  (no vercel.json needed)
  * Handles do_POST, do_OPTIONS, do_GET on whatever path arrives
  * Writes Access-Control-Allow-Origin: * on EVERY response

## Files
  api/index.py        the handler (this folder)
  api/telemetry.json  the dataset
  requirements.txt    empty (stdlib only)

## Deploy
If you already have a repo for this:
  rm -f vercel.json                 # remove old routing
  # replace api/index.py with the new file in this folder
  # empty requirements.txt
  git add -A
  git commit -m "use native Vercel handler"
  git push

Vercel will auto-redeploy on push. After 30–60 s your endpoint is live at:
  https://<your-project>.vercel.app/api

## Verify
URL=https://<your-project>.vercel.app/api

# 1. POST should return JSON metrics
curl -s -X POST "$URL" -H "Content-Type: application/json" \
  -d '{"regions":["apac","amer"],"threshold_ms":187}' | python3 -m json.tool

# Expected (computed from your telemetry):
# {
#   "apac": {"avg_latency": 154.9,  "p95_latency": 192.42, "avg_uptime": 98.252, "breaches": 2},
#   "amer": {"avg_latency": 163.6,  "p95_latency": 215.61, "avg_uptime": 98.464, "breaches": 3}
# }

# 2. OPTIONS preflight should return CORS headers
curl -sI -X OPTIONS "$URL" \
  -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: POST" | grep -i access-control
# Expected:
#   Access-Control-Allow-Origin: *
#   Access-Control-Allow-Methods: POST, OPTIONS, GET
#   Access-Control-Allow-Headers: *

# 3. GET should also work (sanity)
curl -s "$URL"

## Submit
Paste:  https://<your-project>.vercel.app/api
