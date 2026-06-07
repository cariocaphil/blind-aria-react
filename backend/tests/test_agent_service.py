from app.services.agent_service import determine_comparison_target, select_recordings


class TestDetermineComparisonTarget:
    def test_known_work_prompt_vissi_darte(self):
        # Arrange
        prompt = "Find 5 versions of Vissi d'arte"

        # Act
        target = determine_comparison_target(prompt)

        # Assert
        assert target == "Vissi d'arte"

    def test_known_work_prompt_nessun_dorma(self):
        # Arrange
        prompt = "Find 4 versions of Nessun dorma"

        # Act
        target = determine_comparison_target(prompt)

        # Assert
        assert target == "Nessun dorma"

    def test_discovery_prompt_verismo(self):
        # Arrange
        prompt = "Give me a verismo aria in historical recordings"

        # Act
        target = determine_comparison_target(prompt)

        # Assert
        assert target == "Vissi d'arte"

    def test_discovery_prompt_dramatic_soprano_1920s(self):
        # Arrange
        prompt = "Find a dramatic soprano aria from the 1920s"

        # Act
        target = determine_comparison_target(prompt)

        # Assert
        assert target == "Casta Diva"

    def test_unknown_prompt_falls_back_to_default(self):
        # Arrange
        prompt = "Something completely unrelated about jazz fusion"

        # Act
        target = determine_comparison_target(prompt)

        # Assert
        assert target == "Casta Diva"


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
