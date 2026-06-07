import re

from app.models.search_plan import AgentSearchPlan

KNOWN_WORKS = {
    "casta diva": "Casta Diva",
    "vissi d'arte": "Vissi d'arte",
    "vissi d arte": "Vissi d'arte",
    "nessun dorma": "Nessun dorma",
    "gretchen am spinnrade": "Gretchen am Spinnrade",
}

DISCOVERY_TARGETS = {
    "verismo": "Vissi d'arte",
    "dramatic soprano": "Casta Diva",
    "1920": "Casta Diva",
    "puccini": "Nessun dorma",
    "obscure": "Nessun dorma",
    "schubert": "Gretchen am Spinnrade",
    "lied": "Gretchen am Spinnrade",
    "mélodie": "Après un rêve",
    "melodie": "Après un rêve",
    "sacred": "Ave Maria",
}

PERFORMER_EXCLUSION_ALIASES = {
    "callas": ["Callas", "Maria Callas"],
    "pavarotti": ["Pavarotti", "Luciano Pavarotti"],
    "domingo": ["Domingo", "Plácido Domingo"],
    "fischer-dieskau": ["Fischer-Dieskau", "Dietrich Fischer-Dieskau"],
}

HISTORICAL_QUERY_SUFFIXES = [
    "historical recording",
    "old recording",
    "1930s soprano",
    "1940s soprano",
    "1950s soprano",
]

RECENT_QUERY_SUFFIXES = [
    "recent recording",
    "modern recording",
    "2010s",
    "2020s",
]

DECADE_QUERY_SUFFIXES = [
    "1950s",
    "1960s",
    "1970s",
    "1980s",
    "1990s",
]


def interpret_prompt(prompt: str) -> str:
    return prompt.strip()


def determine_comparison_target(prompt: str) -> str:
    normalized = prompt.lower()

    for keyword, work in KNOWN_WORKS.items():
        if keyword in normalized:
            return work

    for keyword, work in DISCOVERY_TARGETS.items():
        if keyword in normalized:
            return work

    return "Casta Diva"


def extract_exclude_terms(prompt: str) -> list[str]:
    normalized = prompt.lower()
    exclude_terms: list[str] = []

    for match in re.finditer(r"(?:without|avoiding|avoid)\s+([^,.]+)", normalized):
        raw_term = match.group(1).strip()
        performer_key = raw_term.split()[-1]

        if performer_key in PERFORMER_EXCLUSION_ALIASES:
            exclude_terms.extend(PERFORMER_EXCLUSION_ALIASES[performer_key])
        else:
            exclude_terms.append(raw_term.title())

    return list(dict.fromkeys(exclude_terms))


def extract_prefer_terms(prompt: str) -> list[str]:
    normalized = prompt.lower()
    prefer_terms: list[str] = []

    if any(
        term in normalized
        for term in ["old", "historical", "era", "1920", "1930", "1940", "1950", "pre-war"]
    ):
        prefer_terms.extend(["historical", "old", "1930", "1940", "1950"])

    if any(term in normalized for term in ["recent", "modern", "2010", "2020"]):
        prefer_terms.extend(["recent", "modern", "2010", "2020"])

    if "decade" in normalized:
        prefer_terms.extend(["1950", "1960", "1970", "1980", "1990"])

    if "live" in normalized:
        prefer_terms.append("live")

    if "studio" in normalized:
        prefer_terms.append("studio")

    return list(dict.fromkeys(prefer_terms))


def build_search_queries(
    comparison_target: str,
    prompt: str,
    count: int,
) -> list[str]:
    normalized = prompt.lower()
    queries = [comparison_target]

    wants_historical = any(
        term in normalized
        for term in ["old", "historical", "era", "1920", "1930", "1940", "1950", "pre-war"]
    )
    wants_recent = any(
        term in normalized for term in ["recent", "modern", "2010", "2020"]
    )
    wants_decades = "decade" in normalized

    if wants_historical:
        queries.extend(
            f"{comparison_target} {suffix}" for suffix in HISTORICAL_QUERY_SUFFIXES
        )

    if wants_recent:
        queries.extend(
            f"{comparison_target} {suffix}" for suffix in RECENT_QUERY_SUFFIXES
        )

    if wants_decades:
        queries.extend(
            f"{comparison_target} {suffix}" for suffix in DECADE_QUERY_SUFFIXES
        )

    if "live" in normalized:
        queries.append(f"{comparison_target} live recording")

    if "studio" in normalized:
        queries.append(f"{comparison_target} studio recording")

    if "contrasting" in normalized or "different" in normalized:
        queries.append(f"{comparison_target} vocal recording")

    unique_queries = list(dict.fromkeys(queries))
    return unique_queries[: max(count, 3)]


class RuleBasedSearchPlanner:
    def build_plan(self, prompt: str, count: int) -> AgentSearchPlan:
        interpreted = interpret_prompt(prompt)
        comparison_target = determine_comparison_target(interpreted)
        exclude_terms = extract_exclude_terms(interpreted)
        prefer_terms = extract_prefer_terms(interpreted)
        search_queries = build_search_queries(comparison_target, interpreted, count)

        rationale_parts = [f"Center comparison on {comparison_target}."]

        if exclude_terms:
            rationale_parts.append(
                f"Exclude recordings matching: {', '.join(exclude_terms)}."
            )

        if prefer_terms:
            rationale_parts.append(
                f"Prefer recordings matching: {', '.join(prefer_terms)}."
            )

        if len(search_queries) > 1:
            rationale_parts.append(f"Run {len(search_queries)} targeted YouTube searches.")

        return AgentSearchPlan(
            comparison_target=comparison_target,
            search_queries=search_queries,
            exclude_terms=exclude_terms,
            prefer_terms=prefer_terms,
            rationale=" ".join(rationale_parts),
        )

    async def create_plan(self, prompt: str, count: int) -> AgentSearchPlan:
        return self.build_plan(prompt, count)
