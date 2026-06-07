from app.services.recording_metadata import (
    derive_decade,
    detect_recording_type,
    enrich_recording_metadata,
    extract_performer,
    resolve_year,
)


class TestYearExtraction:
    def test_extracts_year_from_title_with_parentheses(self):
        year = resolve_year("Maria Callas - Vissi d'arte (1954)")

        assert year == "1954"

    def test_falls_back_to_publication_year(self):
        year = resolve_year(
            "Vissi d'arte",
            published_at="2019-06-12T10:15:30Z",
        )

        assert year == "2019"

    def test_returns_unknown_when_no_year_available(self):
        year = resolve_year("Vissi d'arte")

        assert year == "unknown"


class TestDecadeDerivation:
    def test_derives_1950s_from_1954(self):
        assert derive_decade("1954") == "1950s"

    def test_derives_1930s_from_1932(self):
        assert derive_decade("1932") == "1930s"

    def test_unknown_year_returns_unknown_decade(self):
        assert derive_decade("unknown") == "unknown"


class TestRecordingTypeDetection:
    def test_detects_live_from_concert(self):
        assert detect_recording_type("Tosca - Vissi d'arte live at concert hall") == "live"

    def test_detects_live_from_recital(self):
        assert detect_recording_type("Renata Tebaldi recital performance") == "live"

    def test_detects_studio(self):
        assert detect_recording_type("Vissi d'arte studio recording") == "studio"

    def test_unknown_when_no_signal(self):
        assert detect_recording_type("Vissi d'arte") == "unknown"


class TestPerformerExtraction:
    def test_extracts_performer_from_dash_separator(self):
        performer = extract_performer("Maria Callas - Vissi d'arte")

        assert performer == "Maria Callas"

    def test_extracts_performer_from_sings_pattern(self):
        performer = extract_performer("Renata Tebaldi sings Vissi d'arte")

        assert performer == "Renata Tebaldi"

    def test_falls_back_to_title_when_extraction_is_low_confidence(self):
        performer = extract_performer("A very long unclear title with no performer pattern")

        assert performer == "A very long unclear title with no performer pattern"


class TestEnrichRecordingMetadata:
    def test_returns_required_and_optional_fields(self):
        recording = enrich_recording_metadata(
            video_id="vid-1",
            aria_title="Vissi d'arte",
            source_title="Maria Callas - Vissi d'arte (1954)",
            source_description="Historical studio recording from 1954",
            published_at="2018-01-01T00:00:00Z",
            channel_title="Opera Channel",
        )

        assert recording["id"] == "vid-1"
        assert recording["videoId"] == "vid-1"
        assert recording["ariaTitle"] == "Vissi d'arte"
        assert recording["performer"] == "Maria Callas"
        assert recording["year"] == "1954"
        assert recording["decade"] == "1950s"
        assert recording["recordingType"] == "studio"
        assert recording["sourceTitle"] == "Maria Callas - Vissi d'arte (1954)"
        assert recording["sourceDescription"] == "Historical studio recording from 1954"
        assert recording["channelTitle"] == "Opera Channel"
