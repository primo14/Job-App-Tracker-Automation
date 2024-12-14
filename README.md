# Job Application Tracker Automation

This project automates the process of tracking job applications using the Notion API. It allows you to input job application details and automatically updates a Notion database with the provided information.

## Features

- Input job application details via the command line.
- Automatically extract company name from the application URL.
- Update a Notion database with job application details.

## Prerequisites

- Python 3.9 or higher
- Notion API key
- Notion database ID

## Installation

1. Clone the repository:
   
    ```sh
    git clone https://github.com/yourusername/job-app-tracker-automation.git
    cd job-app-tracker-automation
    ```
    
3. Create and activate a virtual environment:
   
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
   
4. Install the required packages:

    ```sh
   pip install -r requirements.txt
   ```

6. Create a .env file in the project directory and add your Notion API key and database ID:

    ```sh
   API_KEY="your_notion_api_key"
   API_BASE_URL="https://api.notion.com/v1/"
   Page_Id="your_notion_database_id"
   ```
    
## Usage

1. Run the script:

  ```sh
python3 main.py
  ```

2. Enter parameters when prompted

