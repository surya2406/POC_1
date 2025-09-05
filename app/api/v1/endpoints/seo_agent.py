from typing import Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
# from app.agents.graph import workflow
from app.core.settings import get_settings
from app.services.runner import run_agent
from app.agents.agent import react_agent

router = APIRouter()

class AgentRequest(BaseModel):
    query: str = None
    feedback: str = None
    thread_id: int = None



@router.post("/seo/graph")
async def run_seo_graph_endpoint(req: AgentRequest):
    """Run the LangGraph with agent_1 and agent_2"""
    try:
        result=await run_agent(react_agent,req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "SEO graph executed successfully", "result": result}

