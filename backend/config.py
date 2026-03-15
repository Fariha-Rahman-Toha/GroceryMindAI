import os
from dotenv import load_dotenv

load_dotenv()

# Azure endpoints
PROJECT_ENDPOINT            = os.getenv("PROJECT_ENDPOINT")
AZURE_OPENAI_ENDPOINT       = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_AI_API_KEY            = os.getenv("AZURE_AI_API_KEY")
MODEL_DEPLOYMENT_NAME       = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")

# Original 4 agents
DEMAND_FORECAST_AGENT_ID    = os.getenv("DEMAND_FORECAST_AGENT_ID")
EXPIRY_AGENT_ID             = os.getenv("EXPIRY_AGENT_ID")
SUPPLIER_AGENT_ID           = os.getenv("SUPPLIER_AGENT_ID")
REPORTING_AGENT_ID          = os.getenv("REPORTING_AGENT_ID")

# 5 New agents
PRICING_AGENT_ID            = os.getenv("PRICING_AGENT_ID")
STOCK_MONITOR_AGENT_ID      = os.getenv("STOCK_MONITOR_AGENT_ID")
REORDER_AGENT_ID            = os.getenv("REORDER_AGENT_ID")
ANOMALY_DETECTION_AGENT_ID  = os.getenv("ANOMALY_DETECTION_AGENT_ID")
MANAGER_AGENT_ID            = os.getenv("MANAGER_AGENT_ID")