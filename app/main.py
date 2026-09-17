"""
Veridian Corp IT Support Agent - FastAPI Main Application.
Provides RESTful APIs for agent reasoning, ticket queue, knowledge base,
audit logging, and serves the Single-Page Application frontend.
"""

from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.schemas import (
    ProcessRequestPayload, ProcessResponse, Ticket,
    SeedRequest, KnowledgeBaseArticle, PrecedentTicket, AuditStep
)
from app.data.store import store
from app.data.seed_data import KNOWLEDGE_BASE, HISTORICAL_PRECEDENTS
from app.engine.response_builder import response_builder

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Agentic IT Support Service for Veridian Corp with deterministic policy routing and source citation."
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("app/static/index.html")

@app.post("/api/process", response_model=ProcessResponse)
def process_employee_request(payload: ProcessRequestPayload):
    """
    Process an employee request: classify, lookup KB/precedents, evaluate rules,
    determine decision state, format citations, generate ticket, and append audit log.
    """
    try:
        response = response_builder.process_request(payload)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/api/requests", response_model=List[SeedRequest])
def get_seed_requests():
    """Returns the 15 seed employee requests from Section 1.2."""
    return store.list_requests()

@app.get("/api/tickets", response_model=List[Ticket])
def get_tickets(
    status: Optional[str] = Query("all", description="Status filter: all, active, closed"),
    category: Optional[str] = Query("All", description="Category filter"),
    search: Optional[str] = Query(None, description="Search query")
):
    """Returns tickets in queue (historical TK-1042..TK-1051 and newly generated tickets)."""
    return store.list_tickets(status_filter=status, category_filter=category, search=search)

@app.get("/api/tickets/{ticket_id}", response_model=Ticket)
def get_ticket_detail(ticket_id: str):
    ticket = store.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return ticket

@app.get("/api/audit/{ticket_id}", response_model=List[AuditStep])
def get_audit_trail(ticket_id: str):
    """Returns the immutable append-only audit trail for a ticket."""
    audit = store.get_audit_trail(ticket_id)
    if not audit:
        # Check if ticket exists
        ticket = store.get_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return audit

@app.get("/api/knowledge-base", response_model=List[KnowledgeBaseArticle])
def get_knowledge_base():
    """Returns all Knowledge Base articles and policies (KB-01..10 + ASSET-POLICY)."""
    return list(KNOWLEDGE_BASE.values())

@app.get("/api/precedents", response_model=List[PrecedentTicket])
def get_precedents():
    """Returns historical precedent tickets (TK-1042..TK-1051)."""
    return HISTORICAL_PRECEDENTS

@app.post("/api/reset")
def reset_database():
    """Resets database state back to initial seed."""
    store.reset_to_seed()
    return {"message": "Data store reset to initial seed state successfully.", "status": "success"}

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "company": settings.COMPANY_NAME,
        "timeframe": settings.EXERCISE_WEEK,
        "version": settings.VERSION
    }
