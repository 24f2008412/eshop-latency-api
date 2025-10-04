from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

with open("q-vercel-latency.json") as f:
    telemetry = json.load(f)

df = pd.DataFrame(telemetry)

class InputPayload(BaseModel):
    regions: list[str]
    threshold_ms: float

@app.post("/")
async def check_latency(payload: InputPayload):
    filtered = df[df["region"].isin(payload.regions)]
    results = {}

    for region in payload.regions:
        region_data = filtered[filtered["region"] == region]
        avg_latency = region_data["latency_ms"].mean()
        p95_latency = np.percentile(region_data["latency_ms"], 95)
        avg_uptime = region_data["uptime"].mean()
        breaches = (region_data["latency_ms"] > payload.threshold_ms).sum()

        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 4),
            "breaches": int(breaches)
        }

    return results
