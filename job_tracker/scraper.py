from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from . import config


def get_page_text(url):
    options = Options()
    options.headless = True
    if config.BROWSER_PATH:
        options.binary_location = config.BROWSER_PATH
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        driver.close()
    except Exception as e:
        print(e)
    return soup.get_text(separator=" ", strip=True)
