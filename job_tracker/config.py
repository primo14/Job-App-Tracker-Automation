import os

from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("Notion_API_KEY")
DATABASE_ID = os.getenv("Database_Id")
# Optional: only needed to point Selenium at a non-default Chrome/Chromium/Brave binary.
# ChromeDriver itself is auto-downloaded and managed by webdriver-manager.
BROWSER_PATH = os.getenv("Browser_Executable_Path")
