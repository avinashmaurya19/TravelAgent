"""Unit and integration tests for Travel Policy RAG retriever and grounded tool execution."""

import pytest
from app.rag.retriever import PolicyRetriever, policy_retriever
from app.agent.tools.registry import AVAILABLE_TOOLS, TOOL_SCHEMAS, execute_tool


def test_policy_documents_exist_and_chunked():
    """Verify that all markdown policy files are loaded and correctly section-chunked."""
    retriever = PolicyRetriever()
    assert len(retriever.chunks) >= 8, f"Expected at least 8 chunks, got {len(retriever.chunks)}"

    doc_names = {c.doc_name for c in retriever.chunks}
    assert "airline_baggage_policy.md" in doc_names
    assert "cancellation_policy.md" in doc_names
    assert "refund_policy.md" in doc_names

    for chunk in retriever.chunks:
        assert chunk.doc_name.endswith(".md")
        assert len(chunk.section_title) > 0
        assert len(chunk.content.strip()) > 0


def test_baggage_policy_retrieval():
    """Verify semantic retrieval returns precise baggage limits for IndiGo and Air India."""
    # Test IndiGo baggage
    indigo_results = policy_retriever.search("What is the baggage limit for IndiGo?", top_k=2)
    assert len(indigo_results) >= 1
    top = indigo_results[0]
    assert top.doc_name == "airline_baggage_policy.md"
    assert "15 kg" in top.content
    assert "IndiGo" in top.section_title or "IndiGo" in top.content

    # Test Air India baggage
    ai_results = policy_retriever.search("Air India check-in baggage allowance", top_k=2)
    assert len(ai_results) >= 1
    top_ai = ai_results[0]
    assert "Air India" in top_ai.section_title or "Air India" in top_ai.content
    assert "20 kg" in top_ai.content or "25 kg" in top_ai.content


def test_cancellation_policy_retrieval():
    """Verify retrieval returns exact cancellation fee tiers and grace window."""
    # Test >72h flat cancellation fee
    results = policy_retriever.search("How much is the cancellation fee more than 72 hours before flight?", top_k=2)
    assert len(results) >= 1
    top = results[0]
    assert top.doc_name == "cancellation_policy.md"
    assert "1,500" in top.content

    # Test 24-hour zero-penalty window
    grace_results = policy_retriever.search("24 hour free cancellation zero penalty", top_k=2)
    assert len(grace_results) >= 1
    top_grace = grace_results[0]
    assert "24-Hour" in top_grace.section_title or "24 hours" in top_grace.content
    assert "100%" in top_grace.content


def test_refund_policy_retrieval():
    """Verify refund TAT by payment method and airline cancellation compensation."""
    # Test UPI timeline
    upi_results = policy_retriever.search("How long does UPI refund take to process?", top_k=2)
    assert len(upi_results) >= 1
    top_upi = upi_results[0]
    assert top_upi.doc_name == "refund_policy.md"
    assert "24 to 48" in top_upi.content

    # Test Card timeline
    card_results = policy_retriever.search("Credit card debit card refund timeline", top_k=2)
    assert len(card_results) >= 1
    assert "5 to 7" in card_results[0].content

    # Test airline initiated flight cancellation
    airline_cancel_results = policy_retriever.search("Flight cancelled by airline full refund delay", top_k=2)
    assert len(airline_cancel_results) >= 1
    assert "100%" in airline_cancel_results[0].content


def test_search_travel_policy_tool_via_registry(db_session):
    """Verify search_travel_policy tool is executed via authorized dispatcher with citations."""
    res = execute_tool(
        tool_name="search_travel_policy",
        arguments={"query": "What is the baggage allowance for Akasa Air?", "top_k": 2},
        db=db_session,
    )
    assert res["status"] == "success"
    assert res["results_count"] >= 1
    assert "Akasa Air" in res["policy_context"]
    assert "Source" in res["policy_context"]
    assert len(res["sources"]) >= 1
    assert res["sources"][0]["doc_name"] == "airline_baggage_policy.md"


def test_policy_tool_whitelist_registration():
    """Verify search_travel_policy is registered in whitelist and schema specification."""
    assert "search_travel_policy" in AVAILABLE_TOOLS
    tool_names = [s["function"]["name"] for s in TOOL_SCHEMAS]
    assert "search_travel_policy" in tool_names
