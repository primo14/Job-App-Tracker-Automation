from unittest.mock import MagicMock, patch

from job_tracker.notion_client import build_properties, find_by_url, parse_page


def _base_row(status="Applied"):
    return {
        "role": "Software Engineer",
        "company_name": "Acme Corp",
        "date": "2026-01-01T00:00:00+00:00",
        "priority": "Normal",
        "type": "Full-time",
        "application-link": "https://example.com/job/123",
        "location": "Remote",
        "job-site": "Indeed",
        "notes": "referred by a friend",
        "status": status,
    }


def test_build_properties_maps_all_fields():
    row = _base_row()
    properties = build_properties(row)

    assert properties["Role Name"]["title"][0]["text"]["content"] == "Software Engineer"
    assert properties["Company"]["rich_text"][0]["text"]["content"] == "Acme Corp"
    assert properties["Status"]["status"]["name"] == "Applied"
    assert properties["Priority"]["status"]["name"] == "Normal"
    assert properties["Type"]["multi_select"][0]["name"] == "Full-time"
    assert properties["Application Link"]["url"] == "https://example.com/job/123"
    assert properties["Location"]["rich_text"][0]["text"]["content"] == "Remote"
    assert properties["Job site"]["select"]["name"] == "Indeed"
    assert properties["Notes"]["rich_text"][0]["text"]["content"] == "referred by a friend"
    assert properties["Sent Date"]["date"]["start"] == row["date"]


def test_build_properties_drops_sent_date_for_not_started():
    row = _base_row(status="Not started")
    properties = build_properties(row)

    assert "Sent Date" not in properties
    assert "date" not in row


def test_build_properties_drops_sent_date_for_in_progress():
    row = _base_row(status="In progress")
    properties = build_properties(row)

    assert "Sent Date" not in properties


def test_build_properties_keeps_sent_date_for_applied():
    row = _base_row(status="Applied")
    properties = build_properties(row)

    assert "Sent Date" in properties


def test_find_by_url_sends_url_filter_and_returns_results():
    fake_response = MagicMock()
    fake_response.json.return_value = {"results": [{"id": "page-1"}]}

    with patch("job_tracker.notion_client.requests.post", return_value=fake_response) as mock_post:
        results = find_by_url("https://example.com/job/1")

    assert results == [{"id": "page-1"}]
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["filter"] == {
        "property": "Application Link",
        "url": {"equals": "https://example.com/job/1"},
    }


def test_find_by_url_returns_empty_list_when_no_matches():
    fake_response = MagicMock()
    fake_response.json.return_value = {"results": []}

    with patch("job_tracker.notion_client.requests.post", return_value=fake_response):
        results = find_by_url("https://example.com/job/none")

    assert results == []


def _notion_page(
    role="Backend Engineer",
    company="Acme",
    status="Applied",
    priority="Normal",
    sent_date="2026-01-01",
    link="https://example.com/job/1",
    job_site="Indeed",
):
    return {
        "properties": {
            "Role Name": {"title": [{"plain_text": role}]},
            "Company": {"rich_text": [{"plain_text": company}]},
            "Status": {"status": {"name": status}},
            "Priority": {"status": {"name": priority}},
            "Sent Date": {"date": {"start": sent_date}},
            "Application Link": {"url": link},
            "Job site": {"select": {"name": job_site}},
        }
    }


def test_parse_page_extracts_all_fields():
    parsed = parse_page(_notion_page())

    assert parsed == {
        "role": "Backend Engineer",
        "company_name": "Acme",
        "status": "Applied",
        "priority": "Normal",
        "date": "2026-01-01",
        "application-link": "https://example.com/job/1",
        "job-site": "Indeed",
    }


def test_parse_page_handles_unset_optional_fields():
    page = {
        "properties": {
            "Role Name": {"title": []},
            "Company": {"rich_text": []},
            "Status": {"status": None},
            "Priority": {"status": None},
            "Sent Date": {"date": None},
            "Application Link": {"url": None},
            "Job site": {"select": None},
        }
    }

    parsed = parse_page(page)

    assert parsed["role"] == ""
    assert parsed["company_name"] == ""
    assert parsed["status"] == ""
    assert parsed["priority"] == ""
    assert parsed["date"] is None
    assert parsed["application-link"] is None
    assert parsed["job-site"] == ""
