from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from job_tracker import tracker
from job_tracker.ai_extractor import JobRow


def _fake_job_row():
    return JobRow(role="Backend Engineer", company_name="Acme", type="Full-time", location="Remote")


@patch("job_tracker.tracker.ai_extractor")
@patch("job_tracker.tracker.scraper")
def test_build_row_merges_ai_response_into_defaults(mock_scraper, mock_ai):
    mock_scraper.get_page_text.return_value = "some job description text"
    mock_ai.extract_job_details.return_value = _fake_job_row()

    row = tracker.build_row("https://example.com/job/1", [])

    assert row["role"] == "Backend Engineer"
    assert row["company_name"] == "Acme"
    assert row["type"] == "Full-time"
    assert row["location"] == "Remote"
    assert row["application-link"] == "https://example.com/job/1"
    assert row["status"] == "Applied"  # default, untouched


@patch("job_tracker.tracker.ai_extractor")
@patch("job_tracker.tracker.scraper")
def test_build_row_applies_cli_property_overrides(mock_scraper, mock_ai):
    mock_scraper.get_page_text.return_value = "text"
    mock_ai.extract_job_details.return_value = _fake_job_row()

    row = tracker.build_row(
        "https://example.com/job/1",
        ["status:Interviewing Stage", "notes:phone screen done"],
    )

    assert row["status"] == "Interviewing Stage"
    assert row["notes"] == "phone screen done"


@patch("job_tracker.tracker.ai_extractor")
@patch("job_tracker.tracker.scraper")
def test_build_row_ignores_unknown_property_keys(mock_scraper, mock_ai):
    mock_scraper.get_page_text.return_value = "text"
    mock_ai.extract_job_details.return_value = _fake_job_row()

    row = tracker.build_row("https://example.com/job/1", ["not-a-real-field:whatever"])

    assert "not-a-real-field" not in row


@patch("job_tracker.tracker.ai_extractor")
@patch("job_tracker.tracker.scraper")
def test_build_row_does_not_overwrite_with_empty_value(mock_scraper, mock_ai):
    mock_scraper.get_page_text.return_value = "text"
    mock_ai.extract_job_details.return_value = _fake_job_row()

    # second "notes:" has no value after the colon, so it should not
    # clobber the value set by the first override
    row = tracker.build_row(
        "https://example.com/job/1",
        ["notes:first pass", "notes:"],
    )

    assert row["notes"] == "first pass"


@patch("job_tracker.tracker.ai_extractor")
@patch("job_tracker.tracker.scraper")
def test_build_row_skips_property_with_extra_colon(mock_scraper, mock_ai):
    mock_scraper.get_page_text.return_value = "text"
    mock_ai.extract_job_details.return_value = _fake_job_row()

    # "notes" split on ":" yields 3 parts here, so create_row's
    # `len(key_value) == 2` check silently drops the override
    row = tracker.build_row("https://example.com/job/1", ["notes:call at 3:00pm"])

    assert row["notes"] == ""


@patch("job_tracker.tracker.scraper")
def test_build_row_returns_none_on_access_denied(mock_scraper):
    mock_scraper.get_page_text.return_value = "Access Denied"

    row = tracker.build_row("https://example.com/job/1", [])

    assert row is None


@patch("job_tracker.tracker.ai_extractor")
@patch("job_tracker.tracker.scraper")
def test_build_row_returns_none_when_ai_extraction_fails(mock_scraper, mock_ai):
    mock_scraper.get_page_text.return_value = "text"
    mock_ai.extract_job_details.return_value = None

    row = tracker.build_row("https://example.com/job/1", [])

    assert row is None


def test_add_application_skips_when_url_is_empty():
    with patch("job_tracker.tracker.build_row") as mock_build_row:
        tracker.add_application("", [])
        mock_build_row.assert_not_called()


@patch("job_tracker.tracker.notion_client")
@patch("job_tracker.tracker.build_row")
def test_add_application_skips_notion_call_when_row_is_none(mock_build_row, mock_notion):
    mock_notion.find_by_url.return_value = []
    mock_build_row.return_value = None

    tracker.add_application("https://example.com/job/1", [])

    mock_notion.create_page.assert_not_called()


@patch("job_tracker.tracker.notion_client")
@patch("job_tracker.tracker.build_row")
def test_add_application_creates_notion_page_when_row_built(mock_build_row, mock_notion):
    mock_notion.find_by_url.return_value = []
    fake_row = {"role": "Backend Engineer"}
    mock_build_row.return_value = fake_row

    tracker.add_application("https://example.com/job/1", [])

    mock_notion.create_page.assert_called_once_with(fake_row)


@patch("job_tracker.tracker.notion_client")
@patch("job_tracker.tracker.build_row")
def test_add_application_skips_when_url_already_tracked(mock_build_row, mock_notion):
    mock_notion.find_by_url.return_value = [{"id": "existing-page"}]

    tracker.add_application("https://example.com/job/1", [])

    mock_build_row.assert_not_called()
    mock_notion.create_page.assert_not_called()


@patch("job_tracker.tracker.notion_client")
@patch("job_tracker.tracker.build_row")
def test_add_application_proceeds_when_url_not_tracked(mock_build_row, mock_notion):
    mock_notion.find_by_url.return_value = []
    fake_row = {"role": "Backend Engineer"}
    mock_build_row.return_value = fake_row

    tracker.add_application("https://example.com/job/1", [])

    mock_notion.create_page.assert_called_once_with(fake_row)


def _fake_application(status="Applied", date=None, company_name="Acme", role="Engineer", link="https://example.com/1"):
    return {
        "role": role,
        "company_name": company_name,
        "status": status,
        "priority": "Normal",
        "date": date,
        "application-link": link,
        "job-site": "Indeed",
    }


def test_is_stale_true_for_old_applied_with_no_response():
    old_date = (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
    application = _fake_application(status="Applied", date=old_date)

    assert tracker._is_stale(application, stale_after_days=14) is True


def test_is_stale_false_for_recent_applied():
    recent_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    application = _fake_application(status="Applied", date=recent_date)

    assert tracker._is_stale(application, stale_after_days=14) is False


def test_is_stale_false_for_non_applied_status():
    old_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    application = _fake_application(status="Interviewing Stage", date=old_date)

    assert tracker._is_stale(application, stale_after_days=14) is False


def test_is_stale_false_when_no_date():
    application = _fake_application(status="Applied", date=None)

    assert tracker._is_stale(application, stale_after_days=14) is False


@patch("job_tracker.tracker.notion_client")
def test_summarize_applications_counts_by_status_and_flags_stale(mock_notion, capsys):
    old_date = (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
    recent_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    mock_notion.get_pages.return_value = ["page-1", "page-2", "page-3"]
    mock_notion.parse_page.side_effect = [
        _fake_application(status="Applied", date=old_date, company_name="StaleCo"),
        _fake_application(status="Applied", date=recent_date, company_name="FreshCo"),
        _fake_application(status="Rejected", date=old_date, company_name="RejectCo"),
    ]

    applications = tracker.summarize_applications(stale_after_days=14)

    assert len(applications) == 3
    output = capsys.readouterr().out
    assert "Total applications: 3" in output
    assert "Applied: 2" in output
    assert "Rejected: 1" in output
    assert "StaleCo" in output
    assert "FreshCo" not in output
    assert "RejectCo" not in output
