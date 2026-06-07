import json
import os

import httpx
from pydantic import ValidationError

from app.models.search_plan import AgentSearchPlan
from app.services.planners.rule_based_planner import RuleBasedSearchPlanner

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
REQUEST_TIMEOUT_SECONDS = 15.0

SYSTEM_PROMPT = """You are a classical music comparison planner specializing in vocal repertoire.

Your job is to create a search plan for Blind Aria, an app that compares multiple recordings of ONE musical work in blind mode.

Repertoire includes opera arias, lieder, mélodies, art songs, cantata arias, oratorio arias, sacred vocal music, operetta, zarzuela, and classical vocal repertoire generally.

Rules:
1. Always choose exactly ONE comparison target work.
2. Never return multiple unrelated works.
3. For discovery requests (e.g. "give me a Schubert lied"), choose one representative work.
4. Extract constraints such as historical, modern, live, studio, decades, voice type, and performer exclusions.
5. Generate multiple YouTube-oriented search queries for the single comparison target.
6. Return JSON only.

Output schema:
{
  "comparisonTarget": "Work title",
  "searchQueries": ["query 1", "query 2"],
  "excludeTerms": ["Performer name"],
  "preferTerms": ["historical", "live"],
  "rationale": "Short explanation"
}

Do not search YouTube.
Do not select recordings.
Do not rank recordings.
Only produce the search plan."""


def parse_llm_plan_payload(payload: dict) -> AgentSearchPlan:
    normalized = {
        "comparison_target": payload.get("comparison_target")
        or payload.get("comparisonTarget", ""),
        "search_queries": payload.get("search_queries")
        or payload.get("searchQueries", []),
        "exclude_terms": payload.get("exclude_terms")
        or payload.get("excludeTerms", []),
        "prefer_terms": payload.get("prefer_terms")
        or payload.get("preferTerms", []),
        "rationale": payload.get("rationale", ""),
    }

    plan = AgentSearchPlan.model_validate(normalized)

    if not plan.comparison_target.strip():
        raise ValueError("Missing comparison target")

    if not plan.search_queries:
        raise ValueError("Missing search queries")

    return plan


class LlmSearchPlanner:
    def __init__(
        self,
        *,
        api_key: str,
        fallback: RuleBasedSearchPlanner | None = None,
        model: str | None = None,
    ):
        self.api_key = api_key
        self.fallback = fallback or RuleBasedSearchPlanner()
        self.model = model or os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)

    def build_user_prompt(self, prompt: str, count: int) -> str:
        return (
            f"User request: {prompt}\n"
            f"Requested recording count: {count}\n"
            "Create a search plan for a blind comparison playlist."
        )

    async def request_plan_from_llm(self, prompt: str, count: int) -> AgentSearchPlan:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(
                OPENAI_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "temperature": 0.2,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": self.build_user_prompt(prompt, count),
                        },
                    ],
                },
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        payload = json.loads(content)
        return parse_llm_plan_payload(payload)

    async def create_plan(self, prompt: str, count: int) -> AgentSearchPlan:
        try:
            return await self.request_plan_from_llm(prompt, count)
        except (
            httpx.HTTPError,
            httpx.TimeoutException,
            KeyError,
            json.JSONDecodeError,
            ValidationError,
            ValueError,
            IndexError,
        ):
            return await self.fallback.create_plan(prompt, count)
