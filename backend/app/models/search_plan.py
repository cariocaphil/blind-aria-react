from pydantic import BaseModel, Field


class AgentSearchPlan(BaseModel):
    comparison_target: str
    search_queries: list[str]
    exclude_terms: list[str] = Field(default_factory=list)
    prefer_terms: list[str] = Field(default_factory=list)
    rationale: str = ""
