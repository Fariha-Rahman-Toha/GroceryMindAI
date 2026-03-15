"""
main.py
FastAPI backend — 9 routes, one per agent.

Run locally:  uvicorn main:app --reload --port 8000
Test:         http://localhost:8000/docs
"""

import json
import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent_runner import run_agent
from config import (
    DEMAND_FORECAST_AGENT_ID,
    EXPIRY_AGENT_ID,
    SUPPLIER_AGENT_ID,
    REPORTING_AGENT_ID,
    PRICING_AGENT_ID,
    STOCK_MONITOR_AGENT_ID,
    REORDER_AGENT_ID,
    ANOMALY_DETECTION_AGENT_ID,
    MANAGER_AGENT_ID
)

app = FastAPI(
    title="GroceryMind AI",
    description="Multi-agent grocery inventory management system.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ────────────────────────────────────────────────────────────────────

class AgentRequest(BaseModel):
    query: str

class AgentResponse(BaseModel):
    agent:    str
    query:    str
    response: dict | str
    raw:      str


# ── Helper ────────────────────────────────────────────────────────────────────

def parse(raw: str) -> dict | str:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return raw


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "status":  "running",
        "service": "GroceryMind AI API",
        "agents": {
            "demand_forecast": bool(DEMAND_FORECAST_AGENT_ID),
            "expiry":          bool(EXPIRY_AGENT_ID),
            "supplier":        bool(SUPPLIER_AGENT_ID),
            "reporting":       bool(REPORTING_AGENT_ID),
            "pricing":          bool(PRICING_AGENT_ID),
            "stock_monitor":    bool(STOCK_MONITOR_AGENT_ID),
            "reorder":         bool(REORDER_AGENT_ID),
            "anomaly_detection": bool(ANOMALY_DETECTION_AGENT_ID),
            "manager":         bool(MANAGER_AGENT_ID)
        }
    }


# ── Route 1 — Demand Forecast ─────────────────────────────────────────────────

@app.post("/forecast", response_model=AgentResponse)
def forecast(request: AgentRequest):
    if not DEMAND_FORECAST_AGENT_ID:
        raise HTTPException(500, "DEMAND_FORECAST_AGENT_ID not set in .env")
    raw = run_agent(DEMAND_FORECAST_AGENT_ID, request.query)
    if raw.startswith("ERROR:"):
        raise HTTPException(502, raw)
    return AgentResponse(agent="DemandForecastAgent", query=request.query, response=parse(raw), raw=raw)


# ── Route 2 — Expiry Management ───────────────────────────────────────────────

@app.post("/expiry", response_model=AgentResponse)
def expiry(request: AgentRequest):
    if not EXPIRY_AGENT_ID:
        raise HTTPException(500, "EXPIRY_AGENT_ID not set in .env")
    raw = run_agent(EXPIRY_AGENT_ID, request.query)
    if raw.startswith("ERROR:"):
        raise HTTPException(502, raw)
    return AgentResponse(agent="ExpiryManagementAgent", query=request.query, response=parse(raw), raw=raw)


# ── Route 3 — Supplier ────────────────────────────────────────────────────────

@app.post("/supplier", response_model=AgentResponse)
def supplier(request: AgentRequest):
    if not SUPPLIER_AGENT_ID:
        raise HTTPException(500, "SUPPLIER_AGENT_ID not set in .env")
    raw = run_agent(SUPPLIER_AGENT_ID, request.query)
    if raw.startswith("ERROR:"):
        raise HTTPException(502, raw)
    return AgentResponse(agent="SupplierAgent", query=request.query, response=parse(raw), raw=raw)


# ── Route 4 — Reporting ───────────────────────────────────────────────────────

@app.post("/report", response_model=AgentResponse)
def report(request: AgentRequest):
    if not REPORTING_AGENT_ID:
        raise HTTPException(500, "REPORTING_AGENT_ID not set in .env")
    raw = run_agent(REPORTING_AGENT_ID, request.query)
    if raw.startswith("ERROR:"):
        raise HTTPException(502, raw)
    return AgentResponse(agent="ReportingAgent", query=request.query, response=parse(raw), raw=raw)

# ── Route 5 — Pricing ───────────────────────────────────────────────────────

@app.post("/pricing", response_model=AgentResponse)
def pricing(request: AgentRequest):
    if not PRICING_AGENT_ID:
        raise HTTPException(500, "PRICING_AGENT_ID not set in .env")
    raw = run_agent(PRICING_AGENT_ID, request.query)
    if raw.startswith("ERROR:"):
        raise HTTPException(502, raw)
    return AgentResponse(agent="PricingAgent", query=request.query, response=parse(raw), raw=raw)

# ── Route 6 — Anomaly ───────────────────────────────────────────────────────

@app.post("/anomaly", response_model=AgentResponse)
def anomaly(request: AgentRequest):
    if not ANOMALY_DETECTION_AGENT_ID:
        raise HTTPException(500, "ANOMALY_DETECTION_AGENT_ID not set in .env")
    raw = run_agent(ANOMALY_DETECTION_AGENT_ID, request.query)
    if raw.startswith("ERROR:"):
        raise HTTPException(502, raw)
    return AgentResponse(agent="AnomalyDetectionAgent", query=request.query, response=parse(raw), raw=raw)

# ── Route 7 — Stock Monitor ───────────────────────────────────────────────────────
@app.post("/stock_monitor", response_model=AgentResponse)
def stock_monitor(request: AgentRequest):
    if not STOCK_MONITOR_AGENT_ID:
        raise HTTPException(500, "STOCK_MONITOR_AGENT_ID not set in .env")
    raw = run_agent(STOCK_MONITOR_AGENT_ID, request.query)
    if raw.startswith("ERROR:"):
        raise HTTPException(502, raw)
    return AgentResponse(agent="StockMonitorAgent", query=request.query, response=parse(raw), raw=raw)

# ── Route 8 — Reorder ───────────────────────────────────────────────────────
@app.post("/reorder", response_model=AgentResponse)
def reorder(request: AgentRequest):
    if not REORDER_AGENT_ID:
        raise HTTPException(500, "REORDER_AGENT_ID not set in .env")
    raw = run_agent(REORDER_AGENT_ID, request.query)
    if raw.startswith("ERROR:"):
        raise HTTPException(502, raw)
    return AgentResponse(agent="ReorderAgent", query=request.query, response=parse(raw), raw=raw)

# ── Route 9 — Manager ───────────────────────────────────────────────────────
@app.post("/manager", response_model=AgentResponse)
def manager(request: AgentRequest):
    if not MANAGER_AGENT_ID:
        raise HTTPException(500, "MANAGER_AGENT_ID not set in .env")
    raw = run_agent(MANAGER_AGENT_ID, request.query)
    if raw.startswith("ERROR:"):
        raise HTTPException(502, raw)
    return AgentResponse(agent="ManagerAgent", query=request.query, response=parse(raw), raw=raw)



