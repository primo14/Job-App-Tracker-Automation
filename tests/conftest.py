import os

# job_tracker.config / job_tracker.ai_extractor read these at import time
# (OpenAI() and the Notion headers dict are built at module load), so they
# must be set before any test module imports job_tracker.
os.environ.setdefault("Notion_API_KEY", "test-notion-key")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("Database_Id", "test-database-id")
