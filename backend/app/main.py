from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.query import router as query_router
from app.api.team_insights import router as team_insights_router
import sqlite3
from typing import Dict
import os

app = FastAPI(title="R2S Competition DB")

# Serve Next.js build for root
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend/.next")
public_path = os.path.join(os.path.dirname(__file__), "../../frontend/public")

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
elif os.path.exists(public_path):
    app.mount("/", StaticFiles(directory=public_path, html=True), name="frontend")
else:
    print("WARNING: Frontend build not found. Static files won't be served.")

app.include_router(query_router, prefix="/query")
app.include_router(team_insights_router, prefix="/team-insights")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    team_name = item.get("team_name")
    if not team_name:
        return {"error": "Missing 'team_name' in request"}

    conn = sqlite3.connect("race-to-space.db")
    cursor = conn.cursor()
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

    hybrids_score = row[2] if row[2] is not None else 0
    biprops_score = row[3] if row[3] is not None else 0
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
