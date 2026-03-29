#!/usr/bin/env python3
"""A2A (Agent-to-Agent) server wrapper for TradingAgents.

Exposes TradingAgents as an A2A-compliant agent so OpenFang can dispatch
stock analysis tasks to it. PAPER TRADING ONLY.

Port: 8100
"""

import json
import uuid
import re
import traceback
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="TradingAgents A2A Wrapper")

AGENT_CARD = {
    "name": "trading-agents",
    "description": "Multi-agent LLM trading analysis framework. Deploys analyst teams (fundamental, sentiment, news, technical) for stock evaluation. PAPER TRADING ONLY.",
    "url": "http://localhost:8100",
    "version": "0.2.2",
    "skills": [
        {
            "id": "stock-analysis",
            "name": "Stock Analysis",
            "description": "Analyze a stock ticker with multi-agent team (fundamental, sentiment, news, technical analysts + risk management)",
        },
        {
            "id": "market-research",
            "name": "Market Research",
            "description": "Research market conditions and provide trading insights for a given ticker",
        },
    ],
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "stateTransitionHistory": False,
    },
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
}

tasks: dict[str, dict] = {}


@app.get("/.well-known/agent.json")
async def agent_card():
    return JSONResponse(content=AGENT_CARD)


@app.post("/a2a")
async def handle_a2a_task(request: Request):
    body = await request.json()
    method = body.get("method", "")
    params = body.get("params", {})

    if method == "tasks/send":
        return await send_task(params, body.get("id"))
    elif method == "tasks/get":
        return get_task(params.get("id"), body.get("id"))
    elif method == "tasks/cancel":
        return cancel_task(params.get("id"), body.get("id"))
    else:
        return JSONResponse(content={"jsonrpc": "2.0", "id": body.get("id"), "error": {"code": -32601, "message": f"Unknown method: {method}"}})


def extract_ticker(text: str) -> str:
    """Extract stock ticker from natural language text."""
    # Look for explicit tickers (1-5 uppercase letters)
    match = re.search(r'\b([A-Z]{1,5})\b', text)
    if match:
        return match.group(1)
    # Common company name mappings
    mappings = {"apple": "AAPL", "google": "GOOGL", "microsoft": "MSFT", "amazon": "AMZN",
                "tesla": "TSLA", "nvidia": "NVDA", "meta": "META", "netflix": "NFLX"}
    text_lower = text.lower()
    for name, ticker in mappings.items():
        if name in text_lower:
            return ticker
    return "AAPL"  # Default


async def send_task(params: dict, rpc_id=None):
    message_parts = params.get("message", {}).get("parts", [])
    text = next((p["text"] for p in message_parts if p.get("type") == "text"), "Analyze AAPL")

    task_id = str(uuid.uuid4())
    tasks[task_id] = {"id": task_id, "status": {"state": "working"}, "created": datetime.now(timezone.utc).isoformat()}

    ticker = extract_ticker(text)
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG

        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "ollama"
        config["deep_think_llm"] = "llama3.1:70b-instruct-q4_K_M"
        config["quick_think_llm"] = "qwen2.5-coder:32b-instruct-q4_K_M"
        config["backend_url"] = "http://localhost:11434/v1"
        config["max_debate_rounds"] = 1
        config["max_risk_discuss_rounds"] = 1

        ta = TradingAgentsGraph(debug=False, config=config)
        final_state, decision = ta.propagate(ticker, today)

        # Build comprehensive response with analyst reports, debate, and decision
        sections = [f"**TradingAgents Analysis for {ticker} ({today})**"]

        # Analyst reports
        for report_key, label in [
            ("market_report", "📈 Market/Technical Analysis"),
            ("sentiment_report", "💬 Sentiment Analysis"),
            ("news_report", "📰 News Analysis"),
            ("fundamentals_report", "📊 Fundamentals Analysis"),
        ]:
            report = final_state.get(report_key, "")
            if report:
                sections.append(f"\n## {label}\n{report}")

        # Investment debate (researcher bull vs bear)
        debate = final_state.get("investment_debate_state", {})
        judge = debate.get("judge_decision", "")
        if judge:
            sections.append(f"\n## ⚖️ Investment Debate\n{judge}")

        # Risk assessment debate
        risk = final_state.get("risk_debate_state", {})
        risk_judge = risk.get("judge_decision", "")
        if risk_judge:
            sections.append(f"\n## 🛡️ Risk Assessment\n{risk_judge}")

        # Final recommendation
        sections.append(f"\n## 🎯 Final Recommendation\n{decision}")

        response_text = "\n".join(sections)
    except Exception as e:
        response_text = f"TradingAgents analysis error for {ticker}: {str(e)}\n{traceback.format_exc()}"

    tasks[task_id]["status"] = {"state": "completed"}
    tasks[task_id]["artifacts"] = [{"parts": [{"type": "text", "text": response_text}]}]
    return JSONResponse(content={"jsonrpc": "2.0", "id": rpc_id, "result": tasks[task_id]})


def get_task(task_id: str, rpc_id=None):
    task = tasks.get(task_id)
    if not task:
        return JSONResponse(content={"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32602, "message": "Task not found"}})
    return JSONResponse(content={"jsonrpc": "2.0", "id": rpc_id, "result": task})


def cancel_task(task_id: str, rpc_id=None):
    task = tasks.get(task_id)
    if task:
        task["status"] = {"state": "canceled"}
    return JSONResponse(content={"jsonrpc": "2.0", "id": rpc_id, "result": {"id": task_id, "status": {"state": "canceled"}}})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100)

