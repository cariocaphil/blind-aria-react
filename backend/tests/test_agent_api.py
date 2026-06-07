from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app

RECORDING_FIELDS = {"id", "ariaTitle", "videoId", "performer", "year"}


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def verified_recordings():
    return [
        {
            "id": "vid-1",
            "ariaTitle": "Casta Diva",
            "videoId": "vid-1",
            "performer": "Maria Callas",
            "year": "unknown",
        },
        {
            "id": "vid-2",
            "ariaTitle": "Casta Diva",
            "videoId": "vid-2",
            "performer": "Montserrat Caballé",
            "year": "unknown",
        },
        {
            "id": "vid-3",
            "ariaTitle": "Casta Diva",
            "videoId": "vid-3",
            "performer": "Joan Sutherland",
            "year": "unknown",
        },
        {
            "id": "vid-4",
            "ariaTitle": "Casta Diva",
            "videoId": "vid-4",
            "performer": "Renata Tebaldi",
            "year": "unknown",
        },
        {
            "id": "vid-5",
            "ariaTitle": "Casta Diva",
            "videoId": "vid-5",
            "performer": "Anna Netrebko",
            "year": "unknown",
        },
    ]


def assert_recording_shape(recording: dict) -> None:
    assert set(recording.keys()) >= RECORDING_FIELDS
    for field in RECORDING_FIELDS:
        assert isinstance(recording[field], str)
        assert recording[field]


def get_called_search_queries(mock_search) -> list[str]:
    return [call.args[0] for call in mock_search.call_args_list]


def assert_youtube_search_used_for_target(
    mock_search,
    comparison_target: str,
) -> None:
    mock_search.assert_called()
    called_queries = get_called_search_queries(mock_search)
    assert any(comparison_target in query for query in called_queries)


class TestGeneratePlaylistEndpoint:
    @patch(
        "app.services.agent_service.search_youtube_recordings",
        new_callable=AsyncMock,
    )
    def test_known_work_prompt_returns_verified_recordings(
        self,
        mock_search,
        client,
        verified_recordings,
    ):
        # Arrange
        mock_search.return_value = verified_recordings

        # Act
        response = client.post(
            "/api/agent/generate-playlist",
            json={
                "prompt": "Find 5 versions of Vissi d'arte",
                "count": 5,
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["comparisonTarget"] == "Vissi d'arte"
        assert_youtube_search_used_for_target(mock_search, "Vissi d'arte")
        assert "recordings" in data
        assert len(data["recordings"]) <= 5
        for recording in data["recordings"]:
            assert_recording_shape(recording)
            assert recording["ariaTitle"] == "Vissi d'arte"

    @patch(
        "app.services.agent_service.search_youtube_recordings",
        new_callable=AsyncMock,
    )
    def test_discovery_prompt_returns_verified_recordings(
        self,
        mock_search,
        client,
        verified_recordings,
    ):
        # Arrange
        mock_search.return_value = verified_recordings

        # Act
        response = client.post(
            "/api/agent/generate-playlist",
            json={
                "prompt": "Give me a verismo aria in historical recordings",
                "count": 4,
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["comparisonTarget"] == "Vissi d'arte"
        assert_youtube_search_used_for_target(mock_search, "Vissi d'arte")
        assert len(data["recordings"]) <= 4
        for recording in data["recordings"]:
            assert_recording_shape(recording)
            assert recording["ariaTitle"] == "Vissi d'arte"

    @patch(
        "app.services.agent_service.search_youtube_recordings",
        new_callable=AsyncMock,
    )
    def test_respects_requested_count(
        self,
        mock_search,
        client,
        verified_recordings,
    ):
        # Arrange
        mock_search.return_value = verified_recordings

        # Act
        response = client.post(
            "/api/agent/generate-playlist",
            json={
                "prompt": "Find 5 versions of Casta Diva",
                "count": 3,
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["recordings"]) == 3

    @patch(
        "app.services.agent_service.search_youtube_recordings",
        new_callable=AsyncMock,
    )
    def test_deduplicates_recordings_across_queries(
        self,
        mock_search,
        client,
    ):
        # Arrange
        duplicate = {
            "id": "vid-1",
            "ariaTitle": "Casta Diva",
            "videoId": "vid-1",
            "performer": "Maria Callas",
            "year": "unknown",
        }
        unique = {
            "id": "vid-2",
            "ariaTitle": "Casta Diva",
            "videoId": "vid-2",
            "performer": "Montserrat Caballé",
            "year": "unknown",
        }
        mock_search.return_value = [duplicate, unique]

        # Act
        response = client.post(
            "/api/agent/generate-playlist",
            json={
                "prompt": "Give me a verismo aria in historical recordings",
                "count": 5,
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["comparisonTarget"] == "Vissi d'arte"
        assert_youtube_search_used_for_target(mock_search, "Vissi d'arte")
        recordings = data["recordings"]
        video_ids = [recording["videoId"] for recording in recordings]
        assert len(video_ids) == len(set(video_ids))
