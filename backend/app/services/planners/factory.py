import os

from app.services.planners.base import SearchPlanner
from app.services.planners.llm_search_planner import LlmSearchPlanner
from app.services.planners.rule_based_planner import RuleBasedSearchPlanner


def get_search_planner() -> SearchPlanner:
    api_key = os.getenv("OPENAI_API_KEY")
    fallback = RuleBasedSearchPlanner()

    if api_key:
        return LlmSearchPlanner(api_key=api_key, fallback=fallback)

    return fallback
