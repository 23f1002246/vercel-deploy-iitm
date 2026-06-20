# Q25 — Deploy POST analytics endpoint to Vercel

## Files in this folder (already prepared)
- api/index.py        FastAPI handler (POST /api, CORS, percentile, breaches)
- api/telemetry.json  the dataset
- requirements.txt    fastapi
- vercel.json         routes /(.*) → api/index.py

## 1. Push to a new GitHub repo
```
cd q25_vercel
git init -b main
git add .
git commit -m "Vercel latency endpoint"
git remote add origin https://github.com/<USER>/q25-vercel.git
git push -u origin main
```

## 2. Deploy on Vercel
- vercel.com/new → Sign in with GitHub → Import q25-vercel
- Leave defaults (vercel.json drives config) → Deploy
- Wait ~30 s for the URL, e.g. https://q25-vercel-<user>.vercel.app

## 3. Verify
```
URL=https://q25-vercel-<user>.vercel.app/api
curl -s -X POST "$URL" -H "Content-Type: application/json" \
  -d '{"regions":["apac","amer"],"threshold_ms":187}' | python3 -m json.tool
```
Expected (from your telemetry):
```
{
  "apac": {"avg_latency": 154.9,  "p95_latency": 192.42, "avg_uptime": 98.252, "breaches": 2},
  "amer": {"avg_latency": 163.6,  "p95_latency": 215.61, "avg_uptime": 98.464, "breaches": 3}
}
```

CORS preflight:
```
curl -sI -X OPTIONS "$URL" \
  -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: POST" | grep -i access-control
```
Should include: Access-Control-Allow-Origin: *

## 4. Submit
Paste:  https://q25-vercel-<user>.vercel.app/api

## Common fixes
- 404 on POST → vercel.json missing or wrong → use the one in this folder
- 500 / FileNotFoundError → api/telemetry.json must sit next to api/index.py
- CORS fail → keep the CORSMiddleware block in api/index.py untouched
- Cold start → call once before submitting to warm it up
