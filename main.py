import os
import json
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mcp.server.fastmcp import FastMCP

# ---------- Load wellness tips from JSON file ----------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "wellness_tips.json")

try:
    with open(file_path, "r", encoding="utf-8") as f:
        tips = json.load(f)
except Exception as e:
    tips = {}
    print(f"Error loading wellness_tips.json: {e}")


# ---------- Create MCP server ----------

# HTTP-based MCP server (stateless + JSON response mode)
mcp = FastMCP(
    name="WellnessTipsServer",
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def get_wellness_tips(mood: str) -> List[str]:
    """
    MCP tool: return wellness tips for a given mood.

    This tool will be visible to MCP clients as:
      - name: "get_wellness_tips"
      - argument: "mood" (string)
    """
    mood_norm = mood.lower().strip()

    if mood_norm in tips:
        return tips[mood_norm]

    return [
        "No tips available for this mood.",
        "Try another mood like happy, sad, stressed, angry, anxious, frustrated, confused, or neutral.",
    ]


# ---------- Create FastAPI app (REST + MCP) ----------

app = FastAPI(title="Wellness MCP + REST Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Wellness MCP Server is running.",
        "rest_example": "/tips/happy",
        "mcp_endpoint": "/mcp",
    }


@app.get("/tips/{mood}")
def get_tips_http(mood: str):
    """
    REST version for your Streamlit chatbot.

    This is the HTTP API that your Streamlit app calls via requests.get().
    """
    mood_norm = mood.lower().strip()

    if mood_norm in tips:
        return {"mood": mood_norm, "tips": tips[mood_norm]}
    else:
        return {
            "mood": mood_norm,
            "tips": [
                "No tips available for this mood.",
                "Try another mood like happy, sad, stressed, angry, anxious, frustrated, confused, or neutral.",
            ],
        }


# ---------- Mount MCP HTTP app under /mcp ----------

# Exposes the MCP server at /mcp
# This will respond to MCP JSON-RPC over HTTP (tools/list, tools/call, etc.)
app.mount("/mcp", mcp.streamable_http_app())
