from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import tldextract
import json
from notion_database.properties import Properties

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")
Page_Id = os.getenv("Page_Id")  


row = {
  "role": "Software Engineer",
  "company_name": "Google",
  "date": datetime.now().astimezone(timezone.utc).isoformat(),
  "priority": "Normal",
  "type": "Full-time",
  "application-link": "https://www.google.com",
  "location": "Mountain View, CA",
  "job-site": "Otta",
  "notes": "",
    "status": "Applied"
 }

headers = {
    "Authorization": "Bearer " + API_KEY,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def create_row():
    user_input = input()
    if(user_input == ""):
        print("URL Required. Run script again.")
        return False;
    input_parts = user_input.split(" & ")
    url = input_parts[0]
    row["application-link"] = url
    for part in input_parts[1:]:
        key_value = part.split(":")
        if len(key_value) == 2:
            key, value = key_value
            if key in row:
                row[key] = value

    extracted = tldextract.extract(url)
    row["company_name"] = extracted.domain
    if row["company_name"].__contains__("icims") or row["company_name"].__contains__("workday") or row["company_name"].__contains__("greenhouse"):
       row["company_name"] = extracted.subdomain
    #print(row.company_name)  # Output: example 


def get_pages(num_pages=None):
    url = f"https://api.notion.com/v1/databases/{Page_Id}/query"
    get_all = num_pages is None
    page_size = 100 if get_all else num_pages
    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{Page_Id}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])
    return results

def update_database():
    if create_row() is False:
        return
    data = {
        "Role Name": {"title": [{"text": {"content": row["role"]}}]},
        "Company": {"type": "rich_text", "rich_text":[{"text": {"content": row["company_name"]}}]},
        "Status" :{"type": "status", "status": {"name": row["status"]}},
        "Sent Date": {"type": "date", "date": {"start": row["date"]}},
        "Priority": {"type": "status", "status": {"name": row["priority"]}},
        "Type": {"type": "multi_select", "multi_select":[{"name":row["type"]}]},
        "Application Link": {"type": "url","url": row["application-link"]},
        "Location": {"type": "rich_text", "rich_text": [{"text": {"content":row["location"]} }]},
        "Job site": {"type": "select", "select": {"name": row["job-site"]}},
        "Notes": {"type": "rich_text", "rich_text": [{"text": {"content": row["notes"]}}]},
    }

    url = "https://api.notion.com/v1/pages"
    payload = {"parent": {"database_id": Page_Id},
    "properties": data}
    res = requests.post(url,json=payload,headers=headers)
    if res.status_code == 200:
        print('Page added successfully!')
    else:
        print('Error creating page:', res.text)

print("\nEnter the job details in the following format: <application-link> & <'PropName':'PropValue'> & <'PropName':'PropValue'> ...\n")
update_database()


"""""
pages = get_pages()
for page in pages:
    page_id = page["id"]
    props = page["properties"]
    print(json.dumps(props, indent=2))
    exit()
    """