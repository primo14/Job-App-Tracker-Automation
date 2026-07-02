from unittest.mock import MagicMock, patch

from job_tracker.ai_extractor import JobRow, extract_job_details


def test_extract_job_details_returns_parsed_response():
    fake_parsed = JobRow(role="Data Scientist", company_name="Acme", type="Internship", location="Hybrid")
    fake_completion = MagicMock(choices=[MagicMock(message=MagicMock(parsed=fake_parsed))])

    with patch("job_tracker.ai_extractor.client.beta.chat.completions.parse", return_value=fake_completion):
        result = extract_job_details("some job description text")

    assert result == fake_parsed


def test_extract_job_details_returns_none_when_no_choices():
    fake_completion = MagicMock(choices=[])

    with patch("job_tracker.ai_extractor.client.beta.chat.completions.parse", return_value=fake_completion):
        result = extract_job_details("some job description text")

    assert result is None
