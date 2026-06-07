from app.services.agent_service import (
    create_search_plan,
    determine_comparison_target,
    filter_excluded_recordings,
    rank_by_preferred_terms,
    select_recordings,
)


class TestDetermineComparisonTarget:
    def test_known_work_prompt_vissi_darte(self):
        assert determine_comparison_target("Find 5 versions of Vissi d'arte") == "Vissi d'arte"

    def test_known_work_prompt_nessun_dorma(self):
        assert determine_comparison_target("Find 4 versions of Nessun dorma") == "Nessun dorma"

    def test_discovery_prompt_verismo(self):
        assert (
            determine_comparison_target("Give me a verismo aria in historical recordings")
            == "Vissi d'arte"
        )

    def test_unknown_prompt_falls_back_to_default(self):
        assert (
            determine_comparison_target("Something completely unrelated about jazz fusion")
            == "Casta Diva"
        )


class TestCreateSearchPlan:
    def test_known_work_prompt(self):
        # Arrange
        prompt = "Find 5 versions of Vissi d'arte"

        # Act
        plan = create_search_plan(prompt, count=5)

        # Assert
        assert plan.comparison_target == "Vissi d'arte"
        assert any("Vissi d'arte" in query for query in plan.search_queries)
        assert plan.exclude_terms == []
        assert plan.prefer_terms == []

    def test_old_recordings_with_exclusion(self):
        # Arrange
        prompt = "Give me Vissi d'arte, mostly old recordings, without Callas"

        # Act
        plan = create_search_plan(prompt, count=5)

        # Assert
        assert plan.comparison_target == "Vissi d'arte"
        assert any(
            "historical" in query.lower() or "old" in query.lower()
            for query in plan.search_queries
        )
        assert "Callas" in plan.exclude_terms
        assert "Maria Callas" in plan.exclude_terms
        assert any(
            term in plan.prefer_terms for term in ["historical", "old", "1930", "1940", "1950"]
        )

    def test_recent_recordings_prompt(self):
        # Arrange
        prompt = "Find 5 recent recordings of Vissi d'arte"

        # Act
        plan = create_search_plan(prompt, count=5)

        # Assert
        assert plan.comparison_target == "Vissi d'arte"
        assert any(
            "recent" in query.lower() or "modern" in query.lower()
            for query in plan.search_queries
        )
        assert any(term in plan.prefer_terms for term in ["recent", "modern", "2010", "2020"])

    def test_discovery_then_comparison_prompt(self):
        # Arrange
        prompt = "Give me a verismo aria in historical recordings"

        # Act
        plan = create_search_plan(prompt, count=5)

        # Assert
        assert plan.comparison_target == "Vissi d'arte"
        assert all("Vissi d'arte" in query for query in plan.search_queries)
        assert any(
            "historical" in query.lower() or "old" in query.lower()
            for query in plan.search_queries
        )

    def test_different_decades_prompt(self):
        # Arrange
        prompt = "Find 4 versions of Nessun dorma from different decades"

        # Act
        plan = create_search_plan(prompt, count=4)

        # Assert
        assert plan.comparison_target == "Nessun dorma"
        assert "1950" in plan.prefer_terms
        assert any("1950" in query or "1960" in query for query in plan.search_queries)


class TestFilterExcludedRecordings:
    def _make_candidate(self, video_id: str, performer: str) -> dict:
        return {
            "id": video_id,
            "ariaTitle": "Vissi d'arte",
            "videoId": video_id,
            "performer": performer,
            "year": "unknown",
        }

    def test_removes_recordings_matching_exclude_terms(self):
        # Arrange
        recordings = [
            self._make_candidate("vid-1", "Maria Callas - Vissi d'arte"),
            self._make_candidate("vid-2", "Angela Gheorghiu - Vissi d'arte"),
        ]

        # Act
        filtered = filter_excluded_recordings(recordings, ["Callas", "Maria Callas"])

        # Assert
        assert len(filtered) == 1
        assert filtered[0]["videoId"] == "vid-2"


class TestRankByPreferredTerms:
    def _make_candidate(self, video_id: str, performer: str) -> dict:
        return {
            "id": video_id,
            "ariaTitle": "Vissi d'arte",
            "videoId": video_id,
            "performer": performer,
            "year": "unknown",
        }

    def test_prefers_matching_recordings_first(self):
        # Arrange
        recordings = [
            self._make_candidate("vid-1", "Modern soprano 2020"),
            self._make_candidate("vid-2", "Historical 1950 recording"),
            self._make_candidate("vid-3", "Another modern performance"),
        ]

        # Act
        ranked = rank_by_preferred_terms(recordings, ["historical", "1950"])

        # Assert
        assert ranked[0]["videoId"] == "vid-2"
        assert [recording["videoId"] for recording in ranked[1:]] == ["vid-1", "vid-3"]


class TestSelectRecordings:
    def _make_candidate(self, video_id: str, performer: str) -> dict:
        return {
            "id": video_id,
            "ariaTitle": "Casta Diva",
            "videoId": video_id,
            "performer": performer,
            "year": "unknown",
        }

    def test_removes_duplicate_video_ids(self):
        # Arrange
        candidates = [
            self._make_candidate("vid-1", "Performer A"),
            self._make_candidate("vid-1", "Performer A duplicate"),
            self._make_candidate("vid-2", "Performer B"),
        ]

        # Act
        selected = select_recordings(candidates, count=5)

        # Assert
        assert len(selected) == 2
        assert [recording["videoId"] for recording in selected] == ["vid-1", "vid-2"]

    def test_respects_count_limit(self):
        # Arrange
        candidates = [
            self._make_candidate("vid-1", "Performer A"),
            self._make_candidate("vid-2", "Performer B"),
            self._make_candidate("vid-3", "Performer C"),
            self._make_candidate("vid-4", "Performer D"),
        ]

        # Act
        selected = select_recordings(candidates, count=2)

        # Assert
        assert len(selected) == 2

    def test_preserves_input_order(self):
        # Arrange
        candidates = [
            self._make_candidate("vid-3", "Performer C"),
            self._make_candidate("vid-1", "Performer A"),
            self._make_candidate("vid-2", "Performer B"),
        ]

        # Act
        selected = select_recordings(candidates, count=3)

        # Assert
        assert [recording["videoId"] for recording in selected] == [
            "vid-3",
            "vid-1",
            "vid-2",
        ]
