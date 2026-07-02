import json

import requests

from . import config

NOTION_HEADERS = {
    "Authorization": "Bearer " + config.NOTION_API_KEY,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def get_pages(num_pages=None):
    url = f"https://api.notion.com/v1/databases/{config.DATABASE_ID}/query"
    get_all = num_pages is None
    page_size = 100 if get_all else num_pages
    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=NOTION_HEADERS)
    data = response.json()
    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        response = requests.post(url, json=payload, headers=NOTION_HEADERS)
        data = response.json()
        results.extend(data["results"])
    return results


def find_by_url(url):
    query_url = f"https://api.notion.com/v1/databases/{config.DATABASE_ID}/query"
    payload = {"filter": {"property": "Application Link", "url": {"equals": url}}}
    response = requests.post(query_url, json=payload, headers=NOTION_HEADERS)
    return response.json().get("results", [])


def _extract_title(prop):
    items = prop.get("title") or []
    return items[0]["plain_text"] if items else ""


def _extract_rich_text(prop):
    items = prop.get("rich_text") or []
    return items[0]["plain_text"] if items else ""


def _extract_status(prop):
    status = prop.get("status")
    return status["name"] if status else ""


def _extract_select(prop):
    select = prop.get("select")
    return select["name"] if select else ""


def _extract_date(prop):
    date = prop.get("date")
    return date["start"] if date else None


def parse_page(page):
    props = page.get("properties", {})
    return {
        "role": _extract_title(props.get("Role Name", {})),
        "company_name": _extract_rich_text(props.get("Company", {})),
        "status": _extract_status(props.get("Status", {})),
        "priority": _extract_status(props.get("Priority", {})),
        "date": _extract_date(props.get("Sent Date", {})),
        "application-link": props.get("Application Link", {}).get("url"),
        "job-site": _extract_select(props.get("Job site", {})),
    }


def build_properties(row):
    data = {
        "Role Name": {"title": [{"text": {"content": row["role"]}}]},
        "Company": {"type": "rich_text", "rich_text": [{"text": {"content": row["company_name"]}}]},
        "Status": {"type": "status", "status": {"name": row["status"]}},
        "Sent Date": {"type": "date", "date": {"start": row["date"]}},
        "Priority": {"type": "status", "status": {"name": row["priority"]}},
        "Type": {"type": "multi_select", "multi_select": [{"name": row["type"]}]},
        "Application Link": {"type": "url", "url": row["application-link"]},
        "Location": {"type": "rich_text", "rich_text": [{"text": {"content": row["location"]}}]},
        "Job site": {"type": "select", "select": {"name": row["job-site"]}},
        "Notes": {"type": "rich_text", "rich_text": [{"text": {"content": row["notes"]}}]},
    }
    if data["Status"]["status"]["name"] == "Not started" or data["Status"]["status"]["name"] == "In progress":
        data.pop("Sent Date", None)
        row.pop("date", None)
    return data


def create_page(row):
    properties = build_properties(row)
    print(json.dumps(row, indent=2))
    url = "https://api.notion.com/v1/pages"
    payload = {"parent": {"database_id": config.DATABASE_ID}, "properties": properties}
    res = requests.post(url, json=payload, headers=NOTION_HEADERS)
    if res.status_code == 200:
        print('Page added successfully!')
    else:
        print('Error creating page:', res.text)
