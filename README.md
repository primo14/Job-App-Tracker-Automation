# Job Application Tracker Automation

This project automates the process of tracking job applications using the Notion API. It allows you to input job application details and automatically updates a Notion database with the provided information.

## Features

- Input job application details via the command line.
- Uses AI to obtain info needed to fill tracker from the application URL.
- Update a Notion database with job application details.
- Skips duplicate entries when the same application URL is submitted twice.
- `--list` prints a status breakdown and flags stale "Applied" applications with no response.
  
#### Notion Database:

![screenshot-2025-01-08-22-12-45](https://github.com/user-attachments/assets/16c6f080-808b-4c9b-bbaa-b707873866a7)

Add and set up notion database with my template: 
https://www.notion.so/primo99/Job-Automation-Tracker-Template-175fd2b697e080e491d1cc76e9c8f74c?pvs=4

Make sure you reflect any changes to your database in the code!

## Prerequisites

- Python 3.9 or higher
- Google Chrome, Chromium, or Brave installed (ChromeDriver itself is downloaded and managed automatically)
- Notion API key
- Notion database ID
- OpenAI API key

## Installation

1. Clone the repository:
   
    ```sh
    git clone https://github.com/primo14/Job-App-Tracker-Automation.git
    cd Job-App-Tracker-Automation
    ```
    
2. Create and activate a virtual environment:
   
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
   
3. Install the required packages:

    ```sh
   pip install -r requirements.txt
   ```

4. Create a .env file in the project directory (copy `.env.example` as a starting point) and fill in your keys:

    ```sh
   cp .env.example .env
   ```

    ```sh
   Notion_API_KEY="your_notion_api_key"
   OPENAI_API_KEY="your_openai_api_key"
   Database_Id="your_notion_database_id"
   ```

   `Browser_Executable_Path` is optional — only set it if you want Selenium to use a
   non-default browser (e.g. Brave instead of a standard Chrome install):

    ```sh
   Browser_Executable_Path="/path/to/chrome-or-chromium-binary"
   ```

5. (Optional) The `add-job` script lets you run the tracker as a plain shell command
   from anywhere, instead of `cd`-ing into this repo and running `python3 main.py`
   each time. It hardcodes two absolute paths that need to point at wherever you
   cloned this repo — open `add-job` and update both:

    ```sh
    source /path/to/Job-App-Tracker-Automation/venv/bin/activate
    python3 /path/to/Job-App-Tracker-Automation/main.py ...
    ```

6. Add the `add-job` script to your `$PATH`:

   **Option 1: add this repo's directory to `$PATH`**
   ```sh
   echo 'export PATH="$PATH:/path/to/Job-App-Tracker-Automation"' >> ~/.bashrc
   source ~/.bashrc
   ```

   **Option 2: move `add-job` into a directory already on your `$PATH`**
   ```sh
   sudo mv /path/to/Job-App-Tracker-Automation/add-job /usr/local/bin/add-job
   sudo chmod +x /usr/local/bin/add-job
   ```

## Usage

Run directly with Python:

```sh
python3 main.py <application-url> ["PropName:PropValue" ...]
```

OR, if you've added `add-job` to your `$PATH`:

Use ```add-job``` command followed by parameters

#### Syntax

```sh
example: add-job -a [url] [-s status] [-r role] [-l location] [-p priority] [-t type] [-j job-site] [-n notes]

Options
-h Help.
-a Add a new job application. Required parameter.
-s Add the status of the job application. Options are: 'Not started', 'Applied', 'In progress', 'Responded', 'Rejected', 'Dropped', 'Interviewing Stage'.
-r Add the role of the job application.
-l Add the location of the job application.
-p Add the priority of the job application. Options are: 'High', 'Normal', 'Low'.
-j Add the job site where the job application was found. Options are: 'Indeed', 'NewGrad-jobs', 'Otta', 'Handshake', 'Google Jobs'.
-t Add the type of the job application. Options are: 'Internship', 'Contract', 'Part-time', 'Full-time'.
-n Add notes to the job application.
```

If a URL you already added is submitted again, it's skipped instead of creating a duplicate entry.

#### Summary view

Print a status breakdown of everything in the tracker, and flag "Applied" applications
that haven't had a status update in a while (14 days by default):

```sh
python3 main.py --list
python3 main.py --list --stale-after 7
```
