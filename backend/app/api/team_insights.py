from fastapi import APIRouter
from pydantic import BaseModel
from ..services.ml_insights import get_team_insights

router = APIRouter()

class TeamQuery(BaseModel):
    team_name: str

@router.post("/")
def team_insights(query: TeamQuery):
    return get_team_insights(query.team_name)
