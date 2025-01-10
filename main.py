from ast import arg
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import requests
import tldextract
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from pydantic import BaseModel
from openai import OpenAI
import argparse
import sys

load_dotenv()

Notion_API_KEY = os.getenv("Notion_API_KEY")
OpenAI_API_KEY = os.getenv("OpenAI_API_KEY")
Database_id = os.getenv("Database_Id")  

client = OpenAI()

class JobRow(BaseModel):
    role: str
    company_name: str
    type: str
    location: str

row = {
  "role": "Software Engineer",
  "company_name": "Google",
  "date": datetime.now().astimezone(timezone.utc).isoformat(),
  "priority": "Normal",
  "type": "Full-time",
  "application-link": "https://www.google.com",
  "location": "Mountain View, CA",
  "job-site": "NewGrad-Jobs",
  "notes": "",
  "status": "Applied"
 }

notion_headers = {
    "Authorization": "Bearer " + Notion_API_KEY,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}
def get_all_text_from_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    options = Options()
    options.headless = True
    options.binary_location = "/home/pri/.local/share/flatpak/app/com.brave.Browser/current/active/export/bin/com.brave.Browser"
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    
    #print(f"Using Brave binary at: {options.binary_location}")
    #print(f"Opening URL: {url}")

    driver = webdriver.Chrome(service=ChromeService("/usr/local/bin/chromedriver"), options=options)  # Specify the path to the ChromeDriver binary
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    try:
        driver.close()
    except Exception as e:
        print(e)
    text = soup.get_text(separator=" ", strip=True)
    #print(text)
    return text

def create_row(url,properties):
    if url == "":
        return False
    row["application-link"] = url
    text = get_all_text_from_url(url)
    if text== "Access Denied":
        return False
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        temperature=0.5,
        top_p=0.7,
        messages=[
            {"role": "system", "content": "Extract company name, job/role name, type of role(Full-time,Part-time,Internship or Contract) and job location."
             +"For the job location, check to see if remote or hybrid is an option and add that to the location." 
             + "If the description does not include the word remote or hybrid then do not add it to the location."
             +"Get extract this information from the given text taken from the job description."},
            {"role": "user", "content": text},
        ],
        response_format=JobRow,
    )
    if len(completion.choices) == 0:
        print("No response from AI. Run script again.")
        return False
    ai_query_response = completion.choices[0].message.parsed
    #print(ai_query_response)
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
    """extracted = tldextract.extract(url)
    row["company_name"] = extracted.domain
    if row["company_name"].__contains__("icims") or row["company_name"].__contains__("workday") or row["company_name"].__contains__("greenhouse"):
       row["company_name"] = extracted.subdomain"""
    return True
    #print(row.company_name)  # Output: example 


def get_pages(num_pages=None):
    url = f"https://api.notion.com/v1/databases/{Database_id}/query"
    get_all = num_pages is None
    page_size = 100 if get_all else num_pages
    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=notion_headers)
    data = response.json()
    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{Database_id}/query"
        response = requests.post(url, json=payload, headers=notion_headers)
        data = response.json()
        results.extend(data["results"])
    return results

def update_database(url,properties):
    if create_row(url, properties) is False:
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
    if data["Status"]["status"]["name"] == "Not started" or data["Status"]["status"]["name"] == "In progress":
        data.pop("Sent Date",None)
        row.pop("date",None)
    print(json.dumps(row, indent=2))
    url = "https://api.notion.com/v1/pages"
    payload = {"parent": {"database_id": Database_id},
    "properties": data}
    res = requests.post(url,json=payload,headers=notion_headers)
    if res.status_code == 200:
        print('Page added successfully!')
    else:
        print('Error creating page:', res.text)

#print("\nEnter the job details in the following format: <application-link> & <'PropName':'PropValue'> & <'PropName':'PropValue'> ...\n")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Job Application Tracker")
    parser.add_argument("url", help="The application link",type=str)
    parser.add_argument("properties", nargs="*", help="Additional properties in the format 'PropName:PropValue'")
    args = parser.parse_args()

    update_database(args.url, args.properties)

"""""
pages = get_pages()
for page in pages:
    page_id = page["id"]
    props = page["properties"]
    print(json.dumps(props, indent=2))
    exit()
    """

""""completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Get company name, job/role name, type of role(Full-time,Part-time,Internship or Contract) and job location.If the description does not include the word remote. This is not a remote location.Look for job location. Get this from the job application link."},
            {"role": "user", "content": url},
        ],
        response_format=JobRow,
    )"""