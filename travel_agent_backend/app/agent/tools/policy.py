"""Deterministic policy search tool for answering airline rules with grounded RAG."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.rag.retriever import policy_retriever


class SearchPolicyArgs(BaseModel):
    """Arguments for querying travel policy documents."""
    query: str = Field(..., description="User question or keywords about baggage, cancellation, refund, or airline rules")
    top_k: Optional[int] = Field(default=3, description="Number of relevant policy sections to retrieve")


def search_travel_policy_tool(db: Session, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve grounded airline policy clauses matching user inquiry."""
    args = SearchPolicyArgs.model_validate(arguments)
    chunks = policy_retriever.search(args.query, top_k=args.top_k or 3)
    context = policy_retriever.format_context(chunks)

    return {
        "status": "success",
        "query": args.query,
        "results_count": len(chunks),
        "policy_context": context,
        "sources": [c.to_dict() for c in chunks],
    }
