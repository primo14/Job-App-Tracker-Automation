from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()


class JobRow(BaseModel):
    role: str
    company_name: str
    type: str
    location: str


SYSTEM_PROMPT = (
    "Extract company name, job/role name, type of role(Full-time,Part-time,Internship or Contract) and job location."
    + "For the job location, check to see if remote or hybrid is an option and add that to the location."
    + "If the description does not include the word remote or hybrid then do not add it to the location."
    + "Get extract this information from the given text taken from the job description."
)


def extract_job_details(text):
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        temperature=0.5,
        top_p=0.7,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format=JobRow,
    )
    if len(completion.choices) == 0:
        return None
    return completion.choices[0].message.parsed
