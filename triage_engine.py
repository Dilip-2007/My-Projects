from google import genai
from pydantic import BaseModel, Field
from typing import Literal

from config import GEMINI_API_KEY, DEFAULT_MODEL


# ---------------------------------------
# Structured output schema
# ---------------------------------------

class TriageResult(BaseModel):
    department: Literal[
        "Billing & Finance",
        "Technical Support",
        "Security & Fraud",
        "General Inquiry"
    ]

    priority: Literal[
        "Critical",
        "High",
        "Medium",
        "Low"
    ]

    sentiment: Literal[
        "Angry",
        "Frustrated",
        "Neutral",
        "Pleased"
    ]

    sla_response_hours: Literal[
        "2",
        "6",
        "24",
        "48"
    ]

    reasoning: str = Field(
        description="Short justification of assigned department and urgency."
    )


# ---------------------------------------
# Gemini client
# ---------------------------------------

client = genai.Client(api_key=GEMINI_API_KEY)


# ---------------------------------------
# Triage function
# ---------------------------------------

def classify_ticket(customer_email: str) -> TriageResult:

    prompt = f"""
You are an enterprise customer support triage agent.

Analyze the following customer support email.

Customer email:
----------------
{customer_email}
----------------

Classify the ticket according to these rules.

DEPARTMENTS:
- Billing & Finance: charges, payments, refunds, invoices, subscriptions
- Technical Support: API errors, application problems, bugs, technical failures
- Security & Fraud: unauthorized access, suspicious login, account compromise,
  password attacks, 2FA changes not requested by the user
- General Inquiry: general questions, product information, settings,
  feature questions

PRIORITY:
- Critical: security incidents, fraud, unauthorized transactions,
  serious account compromise
- High: production outage, major technical failure, urgent financial problem
- Medium: normal technical or billing issue
- Low: general questions and non-urgent requests

SENTIMENT:
- Angry: strong anger, threats, demands, accusations
- Frustrated: clearly unhappy or struggling
- Neutral: factual or normal request
- Pleased: positive or appreciative tone

SLA:
- Critical = 2 hours
- High = 6 hours
- Medium = 24 hours
- Low = 48 hours

Return ONLY the required structured JSON.
"""

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": TriageResult,
        }
    )

    return TriageResult.model_validate_json(response.text)
    