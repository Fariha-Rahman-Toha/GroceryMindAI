"""
app.py
GroceryMind AI — Streamlit Frontend
9 Agents: Demand Forecast, Expiry, Supplier, Reporting,
          Pricing, Stock Monitor, Reorder, Anomaly Detection, Manager
"""

import requests
import os
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="GroceryMind AI",
    page_icon="🛒",
    layout="wide",
)

# ── Helper ────────────────────────────────────────────────────────────────────

def call_agent(endpoint: str, query: str) -> dict:
    try:
        resp = requests.post(
            f"{BACKEND_URL}/{endpoint}",
            json={"query": query},
            timeout=300,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        return {"error": "⏱️ Timed out. Agent is taking too long — check backend terminal."}
    except requests.exceptions.ConnectionError:
        return {"error": f"🔌 Cannot connect to backend at {BACKEND_URL}. Make sure uvicorn is running."}
    except Exception as e:
        return {"error": str(e)}


def render_response(data: dict):
    if "error" in data:
        st.error(data["error"])
        return

    if data.get("status") == "error":
        st.error(data.get("raw", "Agent returned an error."))
        return

    response = data.get("response", {})

    if isinstance(response, str):
        if response.startswith("ERROR:"):
            st.error(response)
        else:
            st.write(response)
        with st.expander("🔧 Raw response"):
            st.text(data.get("raw", ""))
        return

    if isinstance(response, dict):

        # ── Summary block ─────────────────────────────────────────────────────
        if "summary" in response:
            st.subheader("📊 Summary")
            summary = response["summary"]
            cols = st.columns(min(len(summary), 5))
            for i, (key, val) in enumerate(summary.items()):
                cols[i % 5].metric(key.replace("_", " ").title(), val)

        # ── Forecast ──────────────────────────────────────────────────────────
        if "forecast_7d" in response:
            st.subheader("📈 Demand Forecast")
            c1, c2, c3 = st.columns(3)
            c1.metric("7-Day Forecast",  f"{response.get('forecast_7d','—')} units")
            c2.metric("14-Day Forecast", f"{response.get('forecast_14d','—')} units")
            c3.metric("30-Day Forecast", f"{response.get('forecast_30d','—')} units")
            st.info(f"**Adjustment:** {response.get('adjustment_reason','')}")
            conf = response.get("confidence", 0)
            st.progress(float(conf) if conf else 0, text=f"Confidence: {conf}")

        # ── Expiry actions ────────────────────────────────────────────────────
        if "actions" in response:
            st.subheader("📋 Actions Required")
            for item in response["actions"]:
                urgency = item.get("urgency", "LOW")
                color   = {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡","LOW":"🟢"}.get(urgency,"⚪")
                action  = item.get("recommended_action", "")
                with st.expander(f"{color} {item.get('product_name', item.get('sku',''))} — {action}"):
                    col1, col2 = st.columns(2)
                    for k, v in item.items():
                        if k in ("batch_id","sku","category","quantity","expiry_date","days_until_expiry","discount_pct","price_label"):
                            col1.write(f"**{k.replace('_',' ').title()}:** {v}")
                        else:
                            col2.write(f"**{k.replace('_',' ').title()}:** {v}")

        # ── Order actions ─────────────────────────────────────────────────────
        if "order_actions" in response:
            st.subheader("📦 Purchase Order Actions")
            for item in response["order_actions"]:
                urgency = item.get("urgency","MONITOR")
                color   = {"CRITICAL":"🔴","URGENT":"🟠","MONITOR":"🟢"}.get(urgency,"⚪")
                with st.expander(f"{color} {item.get('po_id','')} — {item.get('product_name','')}"):
                    for k, v in item.items():
                        st.write(f"**{k.replace('_',' ').title()}:** {v}")

        # ── Supplier rankings ─────────────────────────────────────────────────
        if "supplier_rankings" in response:
            st.subheader("🏆 Supplier Rankings")
            for s in response["supplier_rankings"]:
                flag  = s.get("flag","")
                color = {"At Risk":"🔴","Watch":"🟠","Review":"🟡","Good":"🟢"}.get(flag,"⚪")
                with st.expander(f"{color} {s.get('supplier_name','')} — Score: {s.get('reliability_score','')}"):
                    for k, v in s.items():
                        st.write(f"**{k.replace('_',' ').title()}:** {v}")

        # ── Daily report ──────────────────────────────────────────────────────
        if "executive_summary" in response:
            st.subheader("📰 Executive Summary")
            st.info(response["executive_summary"])
            health = response.get("overall_health","")
            color  = {"CRITICAL":"🔴","AT RISK":"🟠","STABLE":"🟡","GOOD":"🟢"}.get(health,"⚪")
            st.metric("Overall Health", f"{color} {health}")
            if "sales" in response:
                sales = response["sales"]
                c1, c2 = st.columns(2)
                c1.metric("Total Revenue (BDT)", sales.get("total_revenue_bdt","—"))
                c2.metric("Units Sold", sales.get("total_units_sold","—"))
            if "kpis" in response:
                kpis = response["kpis"]
                c1, c2, c3 = st.columns(3)
                c1.metric("✅ On Track", kpis.get("on_track_count","—"))
                c2.metric("⚠️ Warning",  kpis.get("warning_count","—"))
                c3.metric("🔴 Critical", kpis.get("critical_count","—"))

        # ── Pricing recommendations ───────────────────────────────────────────
        if "pricing_recommendations" in response:
            st.subheader("💰 Pricing Recommendations")
            for item in response["pricing_recommendations"]:
                change = item.get("price_change_pct", 0)
                arrow  = "🔺" if change > 0 else "🔻" if change < 0 else "➡️"
                with st.expander(f"{arrow} {item.get('product_name', item.get('sku',''))} — {change:+.1f}%"):
                    col1, col2 = st.columns(2)
                    for k, v in item.items():
                        if k in ("sku","product_name","category","current_price_bdt","recommended_price_bdt","price_change_pct"):
                            col1.write(f"**{k.replace('_',' ').title()}:** {v}")
                        else:
                            col2.write(f"**{k.replace('_',' ').title()}:** {v}")

        # ── Stock monitor ─────────────────────────────────────────────────────
        if "stock_levels" in response:
            st.subheader("📦 Stock Levels")
            for item in response["stock_levels"]:
                status = item.get("status","OK")
                color  = {"CRITICAL":"🔴","LOW":"🟠","OK":"🟢","OUT_OF_STOCK":"⚫"}.get(status,"⚪")
                with st.expander(f"{color} {item.get('product_name', item.get('sku',''))} — {status}"):
                    for k, v in item.items():
                        st.write(f"**{k.replace('_',' ').title()}:** {v}")

        # ── Reorder recommendations ───────────────────────────────────────────
        if "reorder_recommendations" in response:
            st.subheader("🔄 Reorder Recommendations")
            for item in response["reorder_recommendations"]:
                urgency = item.get("urgency","NORMAL")
                color   = {"URGENT":"🔴","SOON":"🟠","NORMAL":"🟢"}.get(urgency,"⚪")
                with st.expander(f"{color} {item.get('product_name', item.get('sku',''))} — Order {item.get('recommended_order_qty','')} units"):
                    for k, v in item.items():
                        st.write(f"**{k.replace('_',' ').title()}:** {v}")

        # ── Anomaly detection ─────────────────────────────────────────────────
        if "anomalies" in response:
            st.subheader("🚨 Anomalies Detected")
            if not response["anomalies"]:
                st.success("✅ No anomalies detected.")
            for item in response["anomalies"]:
                severity = item.get("severity","LOW")
                color    = {"HIGH":"🔴","MEDIUM":"🟠","LOW":"🟡"}.get(severity,"⚪")
                with st.expander(f"{color} {item.get('anomaly_type','')} — {item.get('affected_sku', item.get('description',''))}"):
                    for k, v in item.items():
                        st.write(f"**{k.replace('_',' ').title()}:** {v}")

        # ── Manager digest ────────────────────────────────────────────────────
        if "manager_summary" in response:
            st.subheader("👔 Manager Summary")
            st.info(response["manager_summary"])
            if "top_priorities" in response:
                st.subheader("🎯 Top Priorities")
                for i, p in enumerate(response["top_priorities"], 1):
                    urgency = p.get("urgency","")
                    color   = {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡","LOW":"🟢"}.get(urgency,"⚪")
                    st.write(f"{color} **{i}. {p.get('action','')}** — {p.get('reason','')}")
            if "agent_alerts" in response:
                st.subheader("🤖 Agent Alerts")
                for alert in response["agent_alerts"]:
                    st.warning(f"**{alert.get('agent','')}:** {alert.get('message','')}")

        # ── Fallback for any remaining keys ───────────────────────────────────
        shown = {"summary","actions","order_actions","supplier_rankings","forecast_7d",
                 "forecast_14d","forecast_30d","executive_summary","overall_health",
                 "sales","kpis","waste_summary","stock_health","pricing_recommendations",
                 "stock_levels","reorder_recommendations","anomalies","manager_summary",
                 "top_priorities","agent_alerts","adjustment_reason","confidence"}
        remaining = {k: v for k, v in response.items() if k not in shown}
        if remaining:
            st.subheader("📄 Additional Data")
            st.json(remaining)

    else:
        st.write(response)

    with st.expander("🔧 Raw JSON response"):
        st.json(data)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shopping-cart.png", width=80)
    st.title("GroceryMind AI")
    st.caption("Powered by Azure AI Foundry")
    st.divider()
    st.markdown("**9 Agents**")
    st.markdown("🔮 Demand Forecast")
    st.markdown("⏰ Expiry Management")
    st.markdown("🚚 Supplier Status")
    st.markdown("📊 Daily Report")
    st.markdown("💰 Pricing")
    st.markdown("📦 Stock Monitor")
    st.markdown("🔄 Reorder")
    st.markdown("🚨 Anomaly Detection")
    st.markdown("👔 Manager Digest")
    st.divider()
    try:
        r = requests.get(f"{BACKEND_URL}/", timeout=5)
        d = r.json()
        st.success("✅ Backend connected")
        for name, configured in d.get("agents", {}).items():
            icon = "✅" if configured else "❌"
            st.caption(f"{icon} {name.replace('_',' ').title()}")
    except Exception:
        st.error("❌ Backend not reachable")
        st.caption(f"Expected: {BACKEND_URL}")


# ── Tabs ──────────────────────────────────────────────────────────────────────

st.title("🛒 GroceryMind AI")
st.caption("Multi-agent inventory intelligence for grocery stores — Azure AI Foundry")
st.divider()

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "🔮 Demand Forecast",
    "⏰ Expiry Management",
    "🚚 Supplier Status",
    "📊 Daily Report",
    "💰 Pricing",
    "📦 Stock Monitor",
    "🔄 Reorder",
    "🚨 Anomaly Detection",
    "👔 Manager Digest",
])


# ── Tab 1 — Demand Forecast ───────────────────────────────────────────────────
with tab1:
    st.header("🔮 Demand Forecast Agent")
    st.write("Predicts 7, 14, and 30-day demand for any grocery SKU.")
    cols = st.columns(4)
    for i, sku in enumerate(["RICE-5KG-BAS","BREAD-WHITE-400","MILK-FULL-1L","WATER-BTL-1.5L"]):
        if cols[i].button(sku, key=f"f_{sku}"):
            st.session_state["fq"] = f"Forecast demand for {sku}"
    q = st.text_input("Query", value=st.session_state.get("fq","Forecast demand for RICE-5KG-BAS"), key="q1")
    if st.button("▶ Run Forecast", type="primary", key="btn1"):
        with st.spinner("⏳ Running Demand Forecast Agent — please wait up to 2 minutes..."):
            render_response(call_agent("forecast", q))


# ── Tab 2 — Expiry Management ─────────────────────────────────────────────────
with tab2:
    st.header("⏰ Expiry Management Agent")
    st.write("Scans all inventory batches and recommends markdown, donation, or disposal.")
    cols = st.columns(3)
    for i, (label, query) in enumerate([
        ("Full Scan",       "Run the daily expiry scan for all products"),
        ("Urgent Only",     "Which products need immediate action today?"),
        ("Revenue at Risk", "What is the total revenue at risk from expiring stock?"),
    ]):
        if cols[i].button(label, key=f"e_{i}"):
            st.session_state["eq"] = query
    q = st.text_input("Query", value=st.session_state.get("eq","Run the daily expiry scan for all products"), key="q2")
    if st.button("▶ Run Expiry Scan", type="primary", key="btn2"):
        with st.spinner("⏳ Running Expiry Management Agent — please wait up to 2 minutes..."):
            render_response(call_agent("expiry", q))


# ── Tab 3 — Supplier Status ───────────────────────────────────────────────────
with tab3:
    st.header("🚚 Supplier Status Agent")
    st.write("Tracks purchase orders, flags delays, and ranks supplier reliability.")
    cols = st.columns(3)
    for i, (label, query) in enumerate([
        ("Full Report",    "Run the daily supplier and delivery status report"),
        ("Delayed Orders", "Show me all delayed purchase orders right now"),
        ("Rankings",       "Rank all suppliers from most reliable to least reliable"),
    ]):
        if cols[i].button(label, key=f"s_{i}"):
            st.session_state["sq"] = query
    q = st.text_input("Query", value=st.session_state.get("sq","Run the daily supplier and delivery status report"), key="q3")
    if st.button("▶ Run Supplier Report", type="primary", key="btn3"):
        with st.spinner("⏳ Running Supplier Agent — please wait up to 2 minutes..."):
            render_response(call_agent("supplier", q))


# ── Tab 4 — Daily Report ──────────────────────────────────────────────────────
with tab4:
    st.header("📊 Daily Reporting Agent")
    st.write("Generates the full daily morning digest — sales, KPIs, stock health, and waste.")
    cols = st.columns(3)
    for i, (label, query) in enumerate([
        ("Morning Digest", "Generate the daily morning digest"),
        ("KPI Dashboard",  "Show me all KPIs and which ones need attention"),
        ("Stock Health",   "What is the current stock health across all products?"),
    ]):
        if cols[i].button(label, key=f"r_{i}"):
            st.session_state["rq"] = query
    q = st.text_input("Query", value=st.session_state.get("rq","Generate the daily morning digest"), key="q4")
    if st.button("▶ Generate Report", type="primary", key="btn4"):
        with st.spinner("⏳ Running Reporting Agent — please wait up to 2 minutes..."):
            render_response(call_agent("report", q))


# ── Tab 5 — Pricing ───────────────────────────────────────────────────────────
with tab5:
    st.header("💰 Pricing Agent")
    st.write("Recommends optimal prices based on demand, competition, expiry, and seasonal signals.")
    cols = st.columns(3)
    for i, (label, query) in enumerate([
        ("Full Price Review",   "Run the full pricing review for all products"),
        ("Markdown Candidates", "Which products should be marked down today?"),
        ("Price Increase",      "Which products can support a price increase this week?"),
    ]):
        if cols[i].button(label, key=f"p_{i}"):
            st.session_state["pq"] = query
    q = st.text_input("Query", value=st.session_state.get("pq","Run the full pricing review for all products"), key="q5")
    if st.button("▶ Run Pricing Agent", type="primary", key="btn5"):
        with st.spinner("⏳ Running Pricing Agent — please wait up to 2 minutes..."):
            render_response(call_agent("pricing", q))


# ── Tab 6 — Stock Monitor ─────────────────────────────────────────────────────
with tab6:
    st.header("📦 Stock Monitor Agent")
    st.write("Monitors real-time stock levels across all SKUs and flags critical shortages.")
    cols = st.columns(3)
    for i, (label, query) in enumerate([
        ("Full Stock Report",  "Give me a full stock level report for all products"),
        ("Critical Items",     "Which products are critically low or out of stock?"),
        ("Stock by Category",  "Show me stock levels grouped by category"),
    ]):
        if cols[i].button(label, key=f"sm_{i}"):
            st.session_state["smq"] = query
    q = st.text_input("Query", value=st.session_state.get("smq","Give me a full stock level report for all products"), key="q6")
    if st.button("▶ Run Stock Monitor", type="primary", key="btn6"):
        with st.spinner("⏳ Running Stock Monitor Agent — please wait up to 2 minutes..."):
            render_response(call_agent("stock_monitor", q))


# ── Tab 7 — Reorder ───────────────────────────────────────────────────────────
with tab7:
    st.header("🔄 Reorder Agent")
    st.write("Calculates optimal reorder quantities and timing based on stock levels and demand forecasts.")
    cols = st.columns(3)
    for i, (label, query) in enumerate([
        ("Full Reorder Plan",   "Generate the full reorder plan for all products"),
        ("Urgent Reorders",     "Which products need to be reordered urgently today?"),
        ("Weekly Reorder List", "Give me the reorder list for this week"),
    ]):
        if cols[i].button(label, key=f"ro_{i}"):
            st.session_state["roq"] = query
    q = st.text_input("Query", value=st.session_state.get("roq","Generate the full reorder plan for all products"), key="q7")
    if st.button("▶ Run Reorder Agent", type="primary", key="btn7"):
        with st.spinner("⏳ Running Reorder Agent — please wait up to 2 minutes..."):
            render_response(call_agent("reorder", q))


# ── Tab 8 — Anomaly Detection ─────────────────────────────────────────────────
with tab8:
    st.header("🚨 Anomaly Detection Agent")
    st.write("Detects unusual patterns in sales, stock, waste, and supplier behaviour.")
    cols = st.columns(3)
    for i, (label, query) in enumerate([
        ("Full Anomaly Scan",  "Run a full anomaly detection scan across all data"),
        ("Sales Anomalies",    "Are there any unusual patterns in today's sales data?"),
        ("Supplier Anomalies", "Flag any unusual supplier or delivery behaviour this week"),
    ]):
        if cols[i].button(label, key=f"ad_{i}"):
            st.session_state["adq"] = query
    q = st.text_input("Query", value=st.session_state.get("adq","Run a full anomaly detection scan across all data"), key="q8")
    if st.button("▶ Run Anomaly Detection", type="primary", key="btn8"):
        with st.spinner("⏳ Running Anomaly Detection Agent — please wait up to 2 minutes..."):
            render_response(call_agent("anomaly_detection", q))


# ── Tab 9 — Manager Digest ────────────────────────────────────────────────────
with tab9:
    st.header("👔 Manager Digest Agent")
    st.write("Combines all agent outputs into a single prioritised action plan for the store manager.")
    cols = st.columns(3)
    for i, (label, query) in enumerate([
        ("Morning Briefing",  "Give me the full manager morning briefing"),
        ("Top 5 Actions",     "What are the 5 most important actions I need to take today?"),
        ("End of Day Review", "Generate the end of day summary and tomorrow's priorities"),
    ]):
        if cols[i].button(label, key=f"mg_{i}"):
            st.session_state["mgq"] = query
    q = st.text_input("Query", value=st.session_state.get("mgq","Give me the full manager morning briefing"), key="q9")
    if st.button("▶ Run Manager Digest", type="primary", key="btn9"):
        with st.spinner("⏳ Running Manager Digest Agent — please wait up to 2 minutes..."):
            render_response(call_agent("manager", q))