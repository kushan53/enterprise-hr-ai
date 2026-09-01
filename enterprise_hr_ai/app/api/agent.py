from fastapi import APIRouter, Query, Body
from app.services.agent_service import agent_service
from typing import Optional, Dict, Any

router = APIRouter(prefix="/agent", tags=["Agentic Orchestrator & Policy RAG"])

@router.post("/query")
def agent_query_endpoint(
    query: str = Body(..., embed=True),
    agent_type: str = Body(default="orchestrator", embed=True),
    employee_id: Optional[int] = Body(default=None, embed=True)
):
    """
    Direct endpoint for Agentic HR Assistant & Policy RAG retrieval.
    """
    context = {"employee_id": employee_id} if employee_id else {}
    return agent_service.dispatch_agent_workflow(agent_type=agent_type, query=query, context=context)

@router.get("/policy-rag")
def policy_rag_search(query: str = Query(..., description="HR Policy question")):
    """
    RAG-grounded retrieval over company leave, benefits, and workplace policies.
    """
    return agent_service.query_policy_rag(query)
