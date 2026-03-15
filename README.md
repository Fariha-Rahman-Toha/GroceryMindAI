# 🛒 GroceryMind AI
> **Multi-Agent Grocery Inventory Management System**  
> Built on Azure AI Foundry · GPT-4o-mini · FastAPI · Streamlit

## 📌 Overview

GroceryMind AI is an intelligent grocery store inventory management system that deploys **9 specialised AI agents** to automate the decisions store managers make every day — what to reorder, what to markdown, which suppliers to chase, and what needs urgent attention right now.

Built for grocery retailers in **Dhaka, Bangladesh**, the system accounts for local demand signals including Ramadan, Eid, heatwaves, and seasonal patterns that dramatically affect purchasing behaviour in the region.

Each agent is independently responsible for one domain of store operations. Their outputs feed into a **Manager Digest Agent** that synthesises everything into a single prioritised morning briefing — so a store manager walks in, reads one report, and knows exactly what to do.

---

## 🤖 The 9 Agents

| Agent | Role | Key Output |
|---|---|---|
| 🔮 **Demand Forecast** | Predicts 7/14/30-day demand per SKU | Forecast units + confidence score |
| ⏰ **Expiry Management** | Scans all batches for upcoming expiry | Markdown / Donate / Dispose actions |
| 🚚 **Supplier Status** | Tracks POs, flags delays | Supplier rankings + order actions |
| 📊 **Daily Report** | Morning digest of all KPIs | Executive summary + action items |
| 💰 **Pricing** | Recommends optimal prices | Price changes per SKU |
| 📦 **Stock Monitor** | Real-time stock level tracking | Critical / Low / OK status per SKU |
| 🔄 **Reorder** | Calculates reorder quantities and timing | Reorder plan with urgency flags |
| 🚨 **Anomaly Detection** | Detects unusual patterns in data | Flagged anomalies with severity |
| 👔 **Manager** | Combines all agent outputs | Top 5 priorities for the day |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│              9 tabs · demo queries · live UI             │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP (requests)
┌─────────────────────▼───────────────────────────────────┐
│                   FastAPI Backend                        │
│         9 routes · error handling · JSON parsing        │
└─────────────────────┬───────────────────────────────────┘
                      │ OpenAI Assistants API
┌─────────────────────▼───────────────────────────────────┐
│              Azure AI Foundry Classic Agents             │
│         GPT-4o-mini · Code Interpreter · KB Search      │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│ Demand   │ Expiry   │ Supplier │ Pricing  │  Stock Mon  │
│ Forecast │ Mgmt     │ Status   │ Agent    │  Agent      │
├──────────┴──────────┴──────────┴──────────┴─────────────┤
│ Reorder  │ Anomaly  │ Reporting│ Manager  │             │
│ Agent    │ Detect   │ Agent    │ Digest   │             │
└──────────┴──────────┴──────────┴──────────┴─────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                 Azure AI Search                          │
│   products · suppliers · seasonal signals · expiry      │
│   rules · batch inventory · purchase orders · KPIs      │
└─────────────────────────────────────────────────────────┘
```


## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Azure subscription with AI Foundry access
- Azure AI Foundry project with 9 Classic Agents deployed
- Azure AI Search index with knowledge base files uploaded



## 🧪 Test Queries

| Agent | Example Query |
|---|---|
| Demand Forecast | `Forecast demand for RICE-5KG-BAS` |
| Expiry Management | `Run the daily expiry scan for all products` |
| Supplier Status | `Run the daily supplier and delivery status report` |
| Daily Report | `Generate the daily morning digest` |
| Pricing | `Run the full pricing review for all products` |
| Stock Monitor | `Give me a full stock level report for all products` |
| Reorder | `Generate the full reorder plan for all products` |
| Anomaly Detection | `Run a full anomaly detection scan across all data` |
| Manager Digest | `Give me the full manager morning briefing` |


## 🛒 Store Context

The system is configured for a mid-size grocery store in **Dhaka, Bangladesh** with 12 core SKUs across 6 categories:

| Category | SKUs |
|---|---|
| Dry Goods | Basmati Rice 5kg, Cooking Oil 1L, Sugar 1kg, Red Lentils 1kg |
| Dairy | Full Cream Milk 1L, Eggs 12-pack, Yogurt 500g |
| Bakery | White Bread 400g |
| Beverages | Orange Juice 1L, Water 1.5L |
| Vegetables | Fresh Tomatoes, Onions |
| Snacks | Plain Chips 100g |

Demand signals include **Ramadan (1.5x)**, **Eid ul-Fitr (1.8x)**, **Eid ul-Adha (1.6x)**, **Heatwave (1.9x water)**, and 6 other local signals.

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| AI Platform | Azure AI Foundry — Classic Agents |
| LLM | GPT-4o-mini |
| Agent Tools | Code Interpreter, Azure AI Search |
| Backend | FastAPI, Python 3.11, Uvicorn |
| Frontend | Streamlit |
| Auth | AzureKeyCredential / OpenAI API Key |
| Deployment | Azure Container Apps |
| Dev Tools | VS Code, Microsoft Foundry Extension |
