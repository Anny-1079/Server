import os
import json

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

# stateless_http + json_response is recommended for HTTP transport :contentReference[oaicite:1]{index=1}
mcp = FastMCP(
    name="WellnessTipsServer",
    stateless_http=True,
    json_response=True,
)

@mcp.tool()
def get_wellness_tips(mood: str) -> list[str]:
    """
    MCP tool: return wellness tips for a mood.

    This is what MCP clients (Claude Desktop, MCP Inspector, etc.) will call
    using tools/call with name="get_wellness_tips".
    """
    mood_norm = mood.lower()
    if mood_norm in tips:
        return tips[mood_norm]
    return [
        "No tips available for this mood.",
        "Try another mood like happy, sad, stressed, angry, anxious.",
    ]

# ---------- Create FastAPI app (for your chatbot) ----------

app = FastAPI(title="Wellness MCP + REST Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Wellness MCP Server is running.",
        "rest_example": "/tips/happy",
        "mcp_endpoint": "/mcp",   # <-- MCP HTTP endpoint
    }


@app.get("/tips/{mood}")
def get_tips_http(mood: str):
    """
    REST version for your Streamlit chatbot.

    This keeps exactly the behaviour you had before.
    """
    mood_norm = mood.lower()
    if mood_norm in tips:
        return {"mood": mood_norm, "tips": tips[mood_norm]}
    else:
        return {
            "mood": mood_norm,
            "tips": [
                "No tips available for this mood. "
                "Try another mood like happy, sad, stressed, angry, anxious."
            ],
        }


# ---------- Mount MCP HTTP app under /mcp ----------

# This exposes a full MCP HTTP endpoint at /mcp
# Clients will send JSON-RPC (tools/list, tools/call, etc.) here.
app.mount("/mcp", mcp.streamable_http_app())
