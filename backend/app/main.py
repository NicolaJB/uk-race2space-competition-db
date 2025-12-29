from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.query import router as query_router
from app.api.team_insights import router as team_insights_router
import sqlite3
from typing import Dict

# Create FastAPI app
app = FastAPI(title="R2S Competition DB")

# Include routers
app.include_router(query_router, prefix="/query")
app.include_router(team_insights_router, prefix="/team-insights")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production to your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)


# /query endpoint
@app.post("/query")
async def query_db(item: Dict):
    query_text = item.get("query", "")
    conn = sqlite3.connect("race-to-space.db")
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


# /team-insights endpoint
@app.post("/team-insights")
async def team_insights(item: Dict):
    """
    Return team insights formatted for frontend table and chart.
    Expects JSON body: {"team_name": "Bath"}
    """
    team_name = item.get("team_name")
    if not team_name:
        return {"error": "Missing 'team_name' in request"}

    conn = sqlite3.connect("race-to-space.db")
    cursor = conn.cursor()

    # Aggregate scores in case multiple entries exist per team
    cursor.execute("""
        SELECT t.team_name, e.engine_type,
               SUM(hr.total_score) AS hybrids_score,
               SUM(br.total_score) AS biprops_score
        FROM teams t
        LEFT JOIN hybrids_results hr ON t.team_id = hr.team_id
        LEFT JOIN biprops_results br ON t.team_id = br.team_id
        LEFT JOIN engines e ON e.engine_id = hr.engine_id
        WHERE t.team_name = ?
        GROUP BY t.team_name, e.engine_type
    """, (team_name,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"error": "Team not found"}

    # Safely handle NULL values
    hybrids_score = row[2] if row[2] is not None else 0
    biprops_score = row[3] if row[3] is not None else 0

    # Example AI/ML metric: average of Hybrids and Biprops scores
    ai_ml_score = (hybrids_score + biprops_score) / 2

    return {
        "team_name": row[0],
        "engine_type": row[1] or "N/A",
        "insights": [
            {"metric": "Hybrids Score", "value": hybrids_score},
            {"metric": "Biprops Score", "value": biprops_score},
            {"metric": "AI/ML Score", "value": ai_ml_score},
        ],
    }
