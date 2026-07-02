from collections import Counter
from datetime import datetime, timezone

from . import ai_extractor, notion_client, scraper

DEFAULT_ROW = {
    "role": "Software Engineer",
    "company_name": "Google",
    "priority": "Normal",
    "type": "Full-time",
    "application-link": "https://www.google.com",
    "location": "Mountain View, CA",
    "job-site": "NewGrad-Jobs",
    "notes": "",
    "status": "Applied",
}

STALE_AFTER_DAYS_DEFAULT = 14


def build_row(url, properties):
    row = dict(DEFAULT_ROW)
    row["date"] = datetime.now().astimezone(timezone.utc).isoformat()
    row["application-link"] = url

    text = scraper.get_page_text(url)
    if text == "Access Denied":
        return None

    ai_query_response = ai_extractor.extract_job_details(text)
    if ai_query_response is None:
        print("No response from AI. Run script again.")
        return None

    row["role"] = ai_query_response.role
    row["type"] = ai_query_response.type
    row["location"] = ai_query_response.location
    row["company_name"] = ai_query_response.company_name

    for part in properties:
        key_value = part.split(":")
        if len(key_value) == 2:
            key, value = key_value
            if key in row:
                row[key] = value if value != "" else row[key]

    return row


def add_application(url, properties):
    if url == "":
        return
    existing = notion_client.find_by_url(url)
    if existing:
        print(f"Skipping — {len(existing)} existing application(s) already tracked for this URL.")
        return
    row = build_row(url, properties)
    if row is None:
        return
    notion_client.create_page(row)


def _is_stale(application, stale_after_days):
    if application["status"] != "Applied" or not application["date"]:
        return False
    sent = datetime.fromisoformat(application["date"])
    if sent.tzinfo is None:
        sent = sent.replace(tzinfo=timezone.utc)
    age_days = (datetime.now(timezone.utc) - sent).days
    return age_days >= stale_after_days


def summarize_applications(stale_after_days=STALE_AFTER_DAYS_DEFAULT):
    applications = [notion_client.parse_page(page) for page in notion_client.get_pages()]

    print(f"Total applications: {len(applications)}")
    status_counts = Counter(application["status"] or "(no status)" for application in applications)
    for status, count in status_counts.most_common():
        print(f"  {status}: {count}")

    stale = [application for application in applications if _is_stale(application, stale_after_days)]
    if stale:
        print(f"\nApplied {stale_after_days}+ days ago with no status update ({len(stale)}):")
        for application in stale:
            print(f"  - {application['company_name']} — {application['role']} ({application['application-link']})")

    return applications
