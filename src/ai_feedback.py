import os
import requests

GROQ_API_KEY = "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"  # <-- paste your new Groq API key here
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ─── Prompt Templates ───────────────────────────────────────────────────────────
PROMPT_TEMPLATES_SELF = {
    "missing_skills": (
        "Given the job description:\n{jd}\n\n"
        "And your CV:\n{cv}\n\n"
        "List skills from the JD missing in your CV."
    ),
    "improvement": (
        "Review your CV:\n{cv}\n\n"
        "Suggest improvements to make it more ATS-friendly and appealing "
        "for the job description:\n{jd}\n"
    ),
    "interview_questions": (
        "Based on the gaps between the job description:\n{jd}\n\n"
        "and your CV:\n{cv}\n\n"
        "Generate 5 interview questions to assess you."
    ),
}

PROMPT_EXAMPLE = (
    "Given the job description:\n{jd}\n\n"
    "And this candidate's CV:\n{cv}\n\n"
    "List 5 reasons why this CV is a strong match for the job description."
)

PROMPT_REVISION = (
    "You are a professional CV editor. Given the job description:\n{jd}\n\n"
    "And the candidate's original CV:\n{cv}\n\n"
    "Produce a revised, ATS-friendly CV that maximizes alignment with the JD."
)

# ─── Internal Helper ────────────────────────────────────────────────────────────
def format_llama3_prompt(prompt: str) -> list:
    return [
        {"role": "system", "content": "You are a helpful career advisor."},
        {"role": "user",   "content": prompt}
    ]

def call_groq(prompt: str, model: str = "llama3-70b-8192") -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": format_llama3_prompt(prompt),
        "max_tokens": 1500,
        "temperature": 0.7,
    }
    resp = requests.post(GROQ_API_URL, headers=headers, json=payload)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        # Debug output
        print("Groq API error:", resp.status_code, resp.text)
        return "❌ Error generating response from Groq API"
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()

# ─── Public API ────────────────────────────────────────────────────────────────
def get_self_feedback(jd: str, cv_text: str) -> dict:
    """
    Returns a dict with keys: missing_skills, improvement, interview_questions.
    """
    feedback = {}
    for key, template in PROMPT_TEMPLATES_SELF.items():
        prompt = template.format(jd=jd, cv=cv_text)
        feedback[key] = call_groq(prompt)
    return feedback

def get_example_feedback(jd: str, cv_text: str) -> str:
    """
    Single-string feedback listing reasons why an example CV matches the JD.
    """
    prompt = PROMPT_EXAMPLE.format(jd=jd, cv=cv_text)
    return call_groq(prompt)

def get_revised_cv(jd: str, cv_text: str) -> str:
    """
    Returns a full revised CV text optimized for the job description.
    """
    prompt = PROMPT_REVISION.format(jd=jd, cv=cv_text)
    return call_groq(prompt)