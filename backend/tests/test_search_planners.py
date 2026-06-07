import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.services.planners.factory import get_search_planner
from app.services.planners.llm_search_planner import (
    LlmSearchPlanner,
    parse_llm_plan_payload,
)
from app.services.planners.rule_based_planner import RuleBasedSearchPlanner


class TestParseLlmPlanPayload:
    def test_parses_camel_case_payload(self):
        plan = parse_llm_plan_payload(
            {
                "comparisonTarget": "Gretchen am Spinnrade",
                "searchQueries": [
                    "Gretchen am Spinnrade historical recording",
                    "Gretchen am Spinnrade lied recording",
                ],
                "excludeTerms": [],
                "preferTerms": ["historical"],
                "rationale": "Selected a representative Schubert lied for comparison.",
            }
        )

        assert plan.comparison_target == "Gretchen am Spinnrade"
        assert len(plan.search_queries) == 2
        assert plan.prefer_terms == ["historical"]


class TestRuleBasedSearchPlanner:
    @pytest.mark.asyncio
    async def test_builds_plan_for_known_work(self):
        planner = RuleBasedSearchPlanner()

        plan = await planner.create_plan("Find 5 versions of Vissi d'arte", count=5)

        assert plan.comparison_target == "Vissi d'arte"
        assert plan.search_queries


class TestLlmSearchPlanner:
    @pytest.mark.asyncio
    async def test_returns_llm_plan_when_response_is_valid(self):
        planner = LlmSearchPlanner(api_key="test-key")
        llm_payload = {
            "comparisonTarget": "Gretchen am Spinnrade",
            "searchQueries": [
                "Gretchen am Spinnrade historical recording",
                "Gretchen am Spinnrade lied recording",
            ],
            "excludeTerms": [],
            "preferTerms": ["historical"],
            "rationale": "User requested historical interpretations of a Schubert lied.",
        }

        with patch.object(
            planner,
            "request_plan_from_llm",
            new=AsyncMock(return_value=parse_llm_plan_payload(llm_payload)),
        ):
            plan = await planner.create_plan(
                "Give me a Schubert lied in historical recordings.",
                count=5,
            )

        assert plan.comparison_target == "Gretchen am Spinnrade"
        assert "historical recording" in plan.search_queries[0]
        assert plan.prefer_terms == ["historical"]

    @pytest.mark.asyncio
    async def test_falls_back_when_llm_returns_malformed_json(self):
        fallback = RuleBasedSearchPlanner()
        planner = LlmSearchPlanner(api_key="test-key", fallback=fallback)

        with patch.object(
            planner,
            "request_plan_from_llm",
            new=AsyncMock(side_effect=json.JSONDecodeError("invalid", "doc", 0)),
        ):
            plan = await planner.create_plan(
                "Give me a verismo aria in historical recordings",
                count=4,
            )

        assert plan.comparison_target == "Vissi d'arte"

    @pytest.mark.asyncio
    async def test_falls_back_when_provider_is_unavailable(self):
        fallback = RuleBasedSearchPlanner()
        planner = LlmSearchPlanner(api_key="test-key", fallback=fallback)

        with patch.object(
            planner,
            "request_plan_from_llm",
            new=AsyncMock(side_effect=httpx.TimeoutException("timeout")),
        ):
            plan = await planner.create_plan("Find 5 versions of Vissi d'arte", count=5)

        assert plan.comparison_target == "Vissi d'arte"


class TestPlannerFactory:
    def test_uses_rule_planner_without_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        planner = get_search_planner()

        assert isinstance(planner, RuleBasedSearchPlanner)

    def test_uses_llm_planner_with_api_key(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        planner = get_search_planner()

        assert isinstance(planner, LlmSearchPlanner)
