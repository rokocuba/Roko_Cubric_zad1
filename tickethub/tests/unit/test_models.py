"""
Unit testovi za ticket modele

Generated with AI assistance - GitHub Copilot
Razlog: Standardni pattern za testiranje pydantic modela
"""

import pytest
from src.models.ticket import (
    Ticket,
    TicketListItem,
    TicketDetail,
    PaginatedResponse,
    TicketFilters,
    StatsResponse,
    PriorityEnum,
    StatusEnum,
)


class TestTicketModels:
    """Test klasa za ticket modele"""

    def test_priority_enum_values(self):
        """Test da PriorityEnum ima ispravne vrijednosti"""
        assert PriorityEnum.LOW == "low"
        assert PriorityEnum.MEDIUM == "medium"
        assert PriorityEnum.HIGH == "high"

    def test_status_enum_values(self):
        """Test da StatusEnum ima ispravne vrijednosti"""
        assert StatusEnum.OPEN == "open"
        assert StatusEnum.CLOSED == "closed"

    def test_ticket_creation(self):
        """Test kreiranja osnovnog ticket objekta"""
        ticket_data = {
            "id": 1,
            "title": "Test ticket",
            "status": "open",
            "priority": "high",
            "assignee": "test_user",
        }
        ticket = Ticket(**ticket_data)

        assert ticket.id == 1
        assert ticket.title == "Test ticket"
        assert ticket.status == StatusEnum.OPEN
        assert ticket.priority == PriorityEnum.HIGH
        assert ticket.assignee == "test_user"

    def test_ticket_list_item_title_truncation(self):
        """Test da se dugačak naslov skraćuje na 100 znakova"""
        long_title = "A" * 150  # Naslov od 150 znakova
        ticket_data = {
            "id": 1,
            "title": long_title,
            "status": "open",
            "priority": "low",
        }

        ticket = TicketListItem(**ticket_data)
        assert len(ticket.title) == 100
        assert ticket.title.endswith("...")

    def test_ticket_detail_with_source_data(self):
        """Test TicketDetail modela s source_data"""
        ticket_data = {
            "id": 1,
            "title": "Test ticket",
            "status": "closed",
            "priority": "medium",
            "assignee": "test_user",
            "source_data": {
                "id": 1,
                "todo": "Test ticket",
                "completed": True,
                "userId": 1,
            },
        }

        ticket = TicketDetail(**ticket_data)
        assert ticket.source_data["id"] == 1
        assert ticket.source_data["completed"] is True

    def test_paginated_response(self):
        """Test PaginatedResponse modela"""
        ticket_item = TicketListItem(id=1, title="Test", status="open", priority="low")

        response_data = {
            "items": [ticket_item],
            "total": 100,
            "page": 1,
            "per_page": 30,
            "pages": 4,
        }

        response = PaginatedResponse(**response_data)
        assert len(response.items) == 1
        assert response.total == 100
        assert response.pages == 4

    def test_ticket_filters(self):
        """Test TicketFilters modela"""
        filters = TicketFilters(
            status="open", priority="high", search="test", page=2, per_page=50
        )

        assert filters.status == StatusEnum.OPEN
        assert filters.priority == PriorityEnum.HIGH
        assert filters.search == "test"
        assert filters.page == 2
        assert filters.per_page == 50

    def test_stats_response(self):
        """Test StatsResponse modela"""
        stats_data = {
            "total_tickets": 150,
            "open_tickets": 75,
            "closed_tickets": 75,
            "priority_breakdown": {"low": 50, "medium": 50, "high": 50},
        }

        stats = StatsResponse(**stats_data)
        assert stats.total_tickets == 150
        assert stats.open_tickets == 75
        assert stats.closed_tickets == 75
        assert stats.priority_breakdown["low"] == 50
