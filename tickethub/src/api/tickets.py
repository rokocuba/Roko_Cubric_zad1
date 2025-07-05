"""
API endpointovi za tickete

Autor: Roko Čubrić (roko.cubric@fer.hr)
AI Akademija 2025 - Python Developer Test

Generated with AI assistance - GitHub Copilot
Razlog: Standardni FastAPI router pattern s async endpointovima i vanjskim API integracije
Prompt: "Kreiraj FastAPI router za ticket endpointove s validacijom, error handling, paginacijom i DummyJSON integracijom"
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
import math

from ..models.ticket import (
    Ticket,
    TicketDetail,
    TicketListItem,
    PaginatedResponse,
    TicketFilters,
    StatsResponse,
    StatusEnum,
    PriorityEnum,
)
from ..services.external_api import ticket_transform_service, dummy_json_service

router = APIRouter()


async def get_ticket_filters(
    status: Optional[StatusEnum] = Query(None, description="Filtriraj po statusu"),
    priority: Optional[PriorityEnum] = Query(
        None, description="Filtriraj po prioritetu"
    ),
    q: Optional[str] = Query(
        None, min_length=1, max_length=100, description="Pretraži po nazivu"
    ),
    page: int = Query(1, ge=1, description="Broj stranice"),
    per_page: int = Query(30, ge=1, le=100, description="Broj stavki po stranici"),
) -> TicketFilters:
    """Dependency za parsiranje query parametara"""
    return TicketFilters(
        status=status, priority=priority, search=q, page=page, per_page=per_page
    )


@router.get(
    "/", response_model=PaginatedResponse, summary="Dohvati paginiranu listu ticketa"
)
async def get_tickets(filters: TicketFilters = Depends(get_ticket_filters)):
    """
    Dohvaća paginiranu listu ticketa s opcionalnim filtriranjem.

    - **status**: Filtriraj po statusu (open/closed)
    - **priority**: Filtriraj po prioritetu (low/medium/high)
    - **q**: Pretraži po nazivu ticketa
    - **page**: Broj stranice (default: 1)
    - **per_page**: Broj stavki po stranici (default: 30, max: 100)
    """
    try:
        # Izračunaj skip i limit za paginaciju
        skip = (filters.page - 1) * filters.per_page

        # Ako imamo search query, koristi search endpoint
        if filters.search:
            data = await dummy_json_service.search_todos(
                query=filters.search, limit=filters.per_page, skip=skip
            )
        else:
            # Inače dohvati sve todos
            data = await dummy_json_service.get_todos(limit=filters.per_page, skip=skip)

        # Transformiraj todos u tickete
        todos = data.get("todos", [])
        tickets_data = await ticket_transform_service.transform_todos_to_tickets(todos)

        # Filtriraj po statusu i prioritetu ako je potrebno
        if filters.status or filters.priority:
            filtered_tickets = []
            for ticket_data in tickets_data:
                if filters.status and ticket_data["status"] != filters.status:
                    continue
                if filters.priority and ticket_data["priority"] != filters.priority:
                    continue
                filtered_tickets.append(ticket_data)
            tickets_data = filtered_tickets

        # Kreiraj TicketListItem objekte
        tickets = [TicketListItem(**ticket_data) for ticket_data in tickets_data]

        # Izračunaj ukupan broj stranica
        total = data.get("total", len(tickets))
        pages = math.ceil(total / filters.per_page) if total > 0 else 0

        return PaginatedResponse(
            items=tickets,
            total=total,
            page=filters.page,
            per_page=filters.per_page,
            pages=pages,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/search", response_model=PaginatedResponse, summary="Pretraži tickete")
async def search_tickets(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(30, ge=1, le=100, description="Items per page"),
):
    """
    Pretraži tickete po nazivu.

    - **q**: Search query string (obavezno)
    - **page**: Broj stranice
    - **per_page**: Broj stavki po stranici
    """
    filters = TicketFilters(search=q, page=page, per_page=per_page)
    return await get_tickets(filters)


@router.get(
    "/stats/summary",
    response_model=StatsResponse,
    summary="Statistike svih ticketa",
)
async def get_ticket_stats():
    """
    Dohvaća agregirane statistike svih dostupnih ticketa.

    Bonus feature koji prikazuje:
    - Ukupan broj ticketa
    - Broj otvorenih/zatvorenih ticketa
    - Raspodjelu po prioritetima

    Napomena: Koristi se maksimalno 1000 ticketa zbog API ograničenja, izvršavanje može potrajati par sekundi
    """
    try:
        # Prvo dohvati osnovne info da vidimo ukupan broj
        initial_data = await dummy_json_service.get_todos(limit=1, skip=0)
        total_available = initial_data.get("total", 0)

        # Dohvati sve dostupne todos za točne statistike
        # DummyJSON ograničava na max ~1000, ali pokušajmo dohvatiti sve
        limit = min(total_available, 1000)  # Ne više od 1000 odjednom
        data = await dummy_json_service.get_todos(limit=limit, skip=0)
        todos = data.get("todos", [])

        # Ako nema todos, vrati prazne statistike
        if not todos:
            return StatsResponse(
                total_tickets=0,
                open_tickets=0,
                closed_tickets=0,
                priority_breakdown={"low": 0, "medium": 0, "high": 0},
            )

        # Transformiraj u tickete
        tickets_data = await ticket_transform_service.transform_todos_to_tickets(todos)

        # Izračunaj statistike
        total_tickets = len(tickets_data)
        open_tickets = sum(1 for t in tickets_data if t["status"] == "open")
        closed_tickets = total_tickets - open_tickets

        # Raspodjela po prioritetima
        priority_breakdown = {"low": 0, "medium": 0, "high": 0}
        for ticket_data in tickets_data:
            priority = ticket_data["priority"]
            if priority in priority_breakdown:
                priority_breakdown[priority] += 1

        return StatsResponse(
            total_tickets=total_tickets,
            open_tickets=open_tickets,
            closed_tickets=closed_tickets,
            priority_breakdown=priority_breakdown,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/test", summary="Test endpoint bez vanjskih poziva")
async def test_endpoint():
    """Jednostavan test endpoint da testiram routing"""
    return {"message": "Test works!", "status": "ok"}


@router.get("/mock", summary="Mock endpoint s fake podacima")
async def mock_tickets():
    """Test endpoint s mock podacima da proverim radi li routing"""
    from ..models.ticket import TicketListItem, PaginatedResponse

    # Fake ticket data
    mock_tickets = [
        TicketListItem(id=1, title="Test ticket 1", status="open", priority="high"),
        TicketListItem(id=2, title="Test ticket 2", status="closed", priority="low"),
        TicketListItem(id=3, title="Test ticket 3", status="open", priority="medium"),
    ]

    return PaginatedResponse(
        items=mock_tickets,
        total=3,
        page=1,
        per_page=30,
        pages=1,
    )


@router.get(
    "/{ticket_id}", response_model=TicketDetail, summary="Dohvati detalje ticketa"
)
async def get_ticket_by_id(ticket_id: int):
    """
    Dohvaća detalje specifičnog ticketa uključujući puni JSON iz izvora.

    - **ticket_id**: Jedinstveni identifikator ticketa
    """
    try:
        # Dohvati todo iz DummyJSON
        todo_data = await dummy_json_service.get_todo_by_id(ticket_id)

        # Transformiraj u ticket
        ticket_data = await ticket_transform_service.transform_todo_to_ticket(todo_data)

        # Kreiraj TicketDetail objekt
        return TicketDetail(**ticket_data)

    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(
                status_code=404, detail=f"Ticket with ID {ticket_id} not found"
            )
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
