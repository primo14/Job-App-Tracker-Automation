# Job Application Tracker Automation

This project automates the process of tracking job applications using the Notion API. It allows you to input job application details and automatically updates a Notion database with the provided information.

## Features

- Input job application details via the command line.
- Uses AI to obtain info needed to fill tracker from the application URL.
- Update a Notion database with job application details.
  
#### Notion Database:

![screenshot-2025-01-08-22-12-45](https://github.com/user-attachments/assets/16c6f080-808b-4c9b-bbaa-b707873866a7)

Add and set up notion database with my template: 
https://www.notion.so/primo99/Job-Automation-Tracker-Template-175fd2b697e080e491d1cc76e9c8f74c?pvs=4

Make sure you reflect any changes to your database in the code!

## Prerequisites

- Python 3.9 or higher
- Notion API key
- Notion database ID
- OpenAI API key

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

5. Create a .env file in the project directory and add your Notion API key, OpenAI API Key and database ID:

    ```sh
   Notion_API_KEY="your_notion_api_key"
   OPENAI_API_KEY="your_openai_api_key"
   database_id="your_notion_database_id"
   ```
6. Update your main.py path in add-job script

7. Add add-job script to path

     Option 1. Add current path to $PATH environment
     ```sh
     nano ~/.bashrc
     export PATH="$PATH:/home/pri/Desktop/repos/Job-App-Tracker-Automation"
     ```
     Save the file and reload the shell configuration
       ```sh
         source ~/.bashrc```

     Option 2. Move add-job script to an existing $PATH environment
       ```sh
         sudo mv /current/path/add-job /new/path```
    Ensure the script is executable
       ```sh
          sudo chmod +x /new/path/add-job```
    
## Usage

1. Run the python script from its directory:

  ```sh
   python3 main.py
  ```

2. Enter parameters when prompted

OR

Run script from anywhere:

1. Use ```add-job``` command followed by parameters

#### Syntax

```sh
add-job -a [url] [-s status] [-r role] [-l location] [-p priority] [-t type] [-j job-site] [-n notes]

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
