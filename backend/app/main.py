from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.query import router as query_router
from app.api.team_insights import router as team_insights_router
from app.services.ml_insights import get_team_insights  # <- import the function
import sqlite3
from typing import Dict
import os

# -----------------------
# Configuration
# -----------------------

DB_PATH = "/Users/nicolabuttigieg/PycharmProjects/R2S-CompetitionDB/race-to-space.db"

# -----------------------
# Create FastAPI app
# -----------------------
app = FastAPI(title="R2S Competition DB")

# Include backend API routers
app.include_router(query_router, prefix="/query")
app.include_router(team_insights_router, prefix="/team-insights")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production to your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# API Endpoints
# -----------------------

# /query endpoint (unchanged)
@app.post("/query")
async def query_db(item: Dict):
    query_text = item.get("query", "")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.team_name, e.engine_type,
               hr.total_score AS hybrids_score,
               br.total_score AS biprops_score
        FROM teams t
        LEFT JOIN hybrids_results hr ON t.team_id = hr.team_id
        LEFT JOIN biprops_results br ON t.team_id = br.team_id
        LEFT JOIN engines e ON e.engine_id = hr.engine_id
        WHERE t.team_name LIKE ?
    """, (f"%{query_text}%",))
    rows = cursor.fetchall()
    conn.close()

    results = [
        {
            "team_name": row[0],
            "engine_type": row[1] or "N/A",
            "hybrids_score": row[2] or 0,
            "biprops_score": row[3] or 0
        }
        for row in rows
    ]
    return {"results": results}

# -----------------------
# /team-insights endpoint
# -----------------------
@app.post("/team-insights")
async def team_insights(item: Dict):
    team_name = item.get("team_name")
    if not team_name:
        return {"error": "Missing 'team_name' in request"}

    # Use get_team_insights from ml_insights.py
    result = get_team_insights(team_name)
    return result

# -----------------------
# Run locally
# -----------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
