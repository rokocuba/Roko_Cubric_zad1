"""
Servis za dohvaćanje podataka iz DummyJSON API-ja

Autor: Roko Čubrić (roko.cubric@fer.hr)
AI Akademija 2025 - Python Developer Test

Generated with AI assistance - GitHub Copilot
Razlog: Async HTTP klijent s persistent connection i lifecycle management za rješavanje deadlock problema
Prompt: "Kreiraj async servis za DummyJSON API pozive s httpx, persistent client, error handling i proper lifecycle"
"""

import asyncio
from typing import List, Optional, Dict, Any
import httpx
from fastapi import HTTPException

from ..config import settings
from ..models.ticket import DummyJsonTodo, UserBase


class DummyJsonService:
    """Servis za komunikaciju s DummyJSON API-jem"""

    def __init__(self):
        self.base_url = settings.dummyjson_base_url
        self.timeout = httpx.Timeout(10.0)  # Smanjeni timeout za brže failover
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """Lazy inicijalizacija HTTP klijenta"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            )
        return self._client

    async def close(self):
        """Zatvori HTTP klijent"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _make_request(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Dict[Any, Any]:
        """Pomoćna metoda za HTTP pozive s error handling"""
        try:
            client = await self.get_client()
            response = await client.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"External API error: {e.response.text}",
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to connect to external service: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def get_todos(self, limit: int = 30, skip: int = 0) -> Dict[str, Any]:
        """Dohvati todos iz DummyJSON API-ja"""
        params = {"limit": limit, "skip": skip}
        return await self._make_request("todos", params)

    async def get_todo_by_id(self, todo_id: int) -> Dict[str, Any]:
        """Dohvati specifični todo po ID-u"""
        return await self._make_request(f"todos/{todo_id}")

    async def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Dohvati korisnika po ID-u"""
        return await self._make_request(f"users/{user_id}")

    async def get_users(self, limit: int = 30, skip: int = 0) -> Dict[str, Any]:
        """Dohvati korisnike iz DummyJSON API-ja"""
        params = {"limit": limit, "skip": skip}
        return await self._make_request("users", params)

    async def search_todos(
        self, query: str, limit: int = 30, skip: int = 0
    ) -> Dict[str, Any]:
        """Pretraži todos po query stringu"""
        params = {"q": query, "limit": limit, "skip": skip}
        return await self._make_request("todos/search", params)


class TicketTransformService:
    """Servis za transformaciju DummyJSON podataka u naše Ticket modele"""

    def __init__(self):
        self.dummy_json_service = DummyJsonService()
        self._user_cache: Dict[int, UserBase] = {}

    async def _get_user_cached(self, user_id: int) -> UserBase:
        """Dohvati korisnika s cachingom"""
        if user_id not in self._user_cache:
            try:
                user_data = await self.dummy_json_service.get_user_by_id(user_id)
                self._user_cache[user_id] = UserBase(**user_data)
            except HTTPException:
                # Ako ne možemo dohvatiti korisnika, stvorimo dummy user
                self._user_cache[user_id] = UserBase(
                    id=user_id,
                    username=f"user_{user_id}",
                    firstName="Unknown",
                    lastName="User",
                    email=f"user_{user_id}@example.com",
                )
        return self._user_cache[user_id]

    def _calculate_priority(self, todo_id: int) -> str:
        """Izračunaj prioritet na osnovu ID-a"""
        priority_map = {0: "low", 1: "medium", 2: "high"}
        return priority_map[todo_id % 3]

    def _determine_status(self, completed: bool) -> str:
        """Odredi status na osnovu completed flag-a"""
        return "closed" if completed else "open"

    async def transform_todo_to_ticket(
        self, todo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transformiraj DummyJSON todo u naš Ticket format"""
        user = await self._get_user_cached(todo_data["userId"])

        return {
            "id": todo_data["id"],
            "title": todo_data["todo"],
            "status": self._determine_status(todo_data["completed"]),
            "priority": self._calculate_priority(todo_data["id"]),
            "assignee": user.username,
            "source_data": todo_data,
        }

    async def transform_todos_to_tickets(
        self, todos_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Transformiraj listu todos u tickete paralelno"""
        tasks = [self.transform_todo_to_ticket(todo) for todo in todos_data]
        return await asyncio.gather(*tasks)


# Singleton instanca servisa
dummy_json_service = DummyJsonService()
ticket_transform_service = TicketTransformService()
