"""
Pydantic modeli za TicketHub API

Autor: Roko Čubrić (roko.cubric@fer.hr)
AI Akademija 2025 - Python Developer Test

Generated with AI assistance - GitHub Copilot
Razlog: Pydantic modeli s validacijom, enumerators i dokumentacijom za ticket management
Prompt: "Kreiraj kompletne pydantic modele za ticket management s validacijom, enums i dokumentacijom"
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class PriorityEnum(str, Enum):
    """Enum za prioritet ticketa"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StatusEnum(str, Enum):
    """Enum za status ticketa"""

    OPEN = "open"
    CLOSED = "closed"


class UserBase(BaseModel):
    """Osnovni user model iz DummyJSON"""

    id: int
    username: str
    firstName: str
    lastName: str
    email: str

    class Config:
        from_attributes = True


class DummyJsonTodo(BaseModel):
    """Model za todo objekt iz DummyJSON API-ja"""

    id: int
    todo: str
    completed: bool
    userId: int

    class Config:
        from_attributes = True


class TicketBase(BaseModel):
    """Osnovni ticket model"""

    title: str = Field(..., min_length=1, max_length=500, description="Naslov ticketa")
    status: StatusEnum = Field(..., description="Status ticketa (open/closed)")
    priority: PriorityEnum = Field(
        ..., description="Prioritet ticketa (low/medium/high)"
    )
    assignee: str = Field(
        ..., min_length=1, max_length=100, description="Korisničko ime assigned osoby"
    )


class Ticket(TicketBase):
    """Kompletni ticket model s ID-om"""

    id: int = Field(..., gt=0, description="Jedinstveni identifikator ticketa")

    @validator("priority", pre=True)
    def calculate_priority(cls, v, values):
        """Izračunaj prioritet na osnovu ID-a ako nije eksplicitno postavljen"""
        if "id" in values and v is None:
            ticket_id = values["id"]
            priority_map = {
                0: PriorityEnum.LOW,
                1: PriorityEnum.MEDIUM,
                2: PriorityEnum.HIGH,
            }
            return priority_map[ticket_id % 3]
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Fix login issue",
                "status": "open",
                "priority": "high",
                "assignee": "john_doe",
            }
        }


class TicketListItem(BaseModel):
    """Ticket model za paginiranu listu (s ograničenim opisom)"""

    id: int = Field(..., gt=0, description="Jedinstveni identifikator ticketa")
    title: str = Field(..., description="Naslov ticketa (ograničen na 100 znakova)")
    status: StatusEnum = Field(..., description="Status ticketa")
    priority: PriorityEnum = Field(..., description="Prioritet ticketa")

    @validator("title")
    def limit_title_length(cls, v):
        """Ograniči naslov na maksimalno 100 znakova"""
        if len(v) > 100:
            return v[:97] + "..."
        return v

    class Config:
        from_attributes = True


class TicketDetail(Ticket):
    """Detaljni ticket model s punim JSON-om iz izvora"""

    source_data: dict = Field(..., description="Puni JSON iz DummyJSON API-ja")
    created_at: Optional[datetime] = Field(None, description="Datum kreiranja")
    updated_at: Optional[datetime] = Field(None, description="Datum zadnje izmjene")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Fix login issue",
                "status": "open",
                "priority": "high",
                "assignee": "john_doe",
                "source_data": {
                    "id": 1,
                    "todo": "Fix login issue",
                    "completed": False,
                    "userId": 1,
                },
                "created_at": "2025-07-05T10:00:00Z",
                "updated_at": "2025-07-05T10:00:00Z",
            }
        }


class PaginatedResponse(BaseModel):
    """Model za paginirane odgovore"""

    items: List[TicketListItem] = Field(..., description="Lista ticketa")
    total: int = Field(..., ge=0, description="Ukupan broj ticketa")
    page: int = Field(..., ge=1, description="Trenutna stranica")
    per_page: int = Field(..., ge=1, le=100, description="Broj stavki po stranici")
    pages: int = Field(..., ge=0, description="Ukupan broj stranica")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "title": "Fix login issue",
                        "status": "open",
                        "priority": "high",
                    }
                ],
                "total": 150,
                "page": 1,
                "per_page": 30,
                "pages": 5,
            }
        }


class TicketFilters(BaseModel):
    """Model za filtriranje ticketa"""

    status: Optional[StatusEnum] = Field(None, description="Filtriraj po statusu")
    priority: Optional[PriorityEnum] = Field(
        None, description="Filtriraj po prioritetu"
    )
    search: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Pretraži po nazivu"
    )
    page: int = Field(1, ge=1, description="Broj stranice")
    per_page: int = Field(30, ge=1, le=100, description="Broj stavki po stranici")

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    """Model za statistike (bonus feature)"""

    total_tickets: int = Field(..., ge=0, description="Ukupan broj ticketa")
    open_tickets: int = Field(..., ge=0, description="Broj otvorenih ticketa")
    closed_tickets: int = Field(..., ge=0, description="Broj zatvorenih ticketa")
    priority_breakdown: dict = Field(..., description="Raspodjela po prioritetima")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "total_tickets": 150,
                "open_tickets": 75,
                "closed_tickets": 75,
                "priority_breakdown": {"low": 50, "medium": 50, "high": 50},
            }
        }
