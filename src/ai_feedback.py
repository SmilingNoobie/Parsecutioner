import os
import requests

GROQ_API_KEY = "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"  # <-- paste your new Groq API key here
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Prompt templates
PROMPT_TEMPLATES_SELF = {
    'missing_skills': "Given the job description:\n{jd}\n\nAnd your CV:\n{cv}\n\nList skills from the JD missing in your CV.",
    'improvement': "Review your CV:\n{cv}\n\nSuggest improvements to make it more ATS-friendly and appealing for the job description:\n{jd}\n",
    'interview_questions': "Based on the gaps between the job description:\n{jd}\nand your CV:\n{cv}\n\nGenerate 5 interview questions to assess you."
}

PROMPT_EXAMPLE = (
    "Given the job description:\n{jd}\n\n"
    "And this candidate's CV:\n{cv}\n\n"
    "List 5 reasons why this CV is a strong match for the job description."
)

# Llama 3 specific prompt formatting
def format_llama3_prompt(prompt: str) -> list:
    return [
        {"role": "system", "content": "You are a helpful career advisor."},
        {"role": "user", "content": prompt}
    ]

def call_groq(prompt: str, model: str = "llama3-70b-8192") -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": format_llama3_prompt(prompt),
        "max_tokens": 1000,
        "temperature": 0.7
    }

    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content'].strip()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {resp.text}")
        return "Error generating response"

def get_self_feedback(jd: str, cv_text: str) -> dict:
    return {k: call_groq(template.format(jd=jd, cv=cv_text))
            for k, template in PROMPT_TEMPLATES_SELF.items()}

def get_example_feedback(jd: str, cv_text: str) -> str:
    prompt = PROMPT_EXAMPLE.format(jd=jd, cv=cv_text)
    return call_groq(prompt)
