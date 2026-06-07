from typing import Protocol

from app.models.search_plan import AgentSearchPlan


class SearchPlanner(Protocol):
    async def create_plan(self, prompt: str, count: int) -> AgentSearchPlan:
        ...
