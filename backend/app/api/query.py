from fastapi import APIRouter
import sqlite3

router = APIRouter()

@router.post("/")
async def query_db(item: dict):
    q = item.get("query", "")
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
    """, (f"%{q}%",))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "team_name": row[0],
            "engine_type": row[1] or "N/A",
            "hybrids_score": row[2] or 0,
            "biprops_score": row[3] or 0
        })
    return {"results": results}
