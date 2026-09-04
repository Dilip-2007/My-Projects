from google import genai

from config import GEMINI_API_KEY, DEFAULT_MODEL
from triage_engine import TriageResult


client = genai.Client(api_key=GEMINI_API_KEY)


# ---------------------------------------
# Company policies
# ---------------------------------------

REFUND_POLICY = """
Refund Policy:
- Unauthorized transactions must be investigated immediately.
- The customer should be advised to secure their account.
- Refund eligibility must be verified before promising a completed refund.
- Never claim that money has already been refunded unless confirmed.
"""


SECURITY_POLICY = """
Security Policy:
- If an account may have been compromised, advise the customer to secure
  their account immediately.
- Recommend changing the password.
- Recommend reviewing recent account activity.
- Recommend contacting the security/support team.
- Never ask the customer to provide their password or OTP.
"""


TECHNICAL_POLICY = """
Technical Support Policy:
- Acknowledge the technical problem.
- Explain that the issue is being escalated when appropriate.
- Request useful diagnostic information when necessary.
- Never invent a resolution that has not been confirmed.
"""


GENERAL_POLICY = """
General Inquiry Policy:
- Answer politely and clearly.
- Keep the response concise.
- Provide useful next steps when applicable.
"""


# ---------------------------------------
# Response generator
# ---------------------------------------

def generate_response(
    customer_email: str,
    triage: TriageResult
) -> str:

    if triage.department == "Billing & Finance":
        policy = REFUND_POLICY

    elif triage.department == "Security & Fraud":
        policy = SECURITY_POLICY

    elif triage.department == "Technical Support":
        policy = TECHNICAL_POLICY

    else:
        policy = GENERAL_POLICY

    prompt = f"""
You are a professional enterprise customer support response agent.

Customer email:
----------------
{customer_email}
----------------

Ticket classification:
Department: {triage.department}
Priority: {triage.priority}
Sentiment: {triage.sentiment}
SLA: {triage.sla_response_hours} hours
Reasoning: {triage.reasoning}

Relevant company policy:
----------------
{policy}
----------------

Write a professional, empathetic customer support response.

Requirements:
1. Acknowledge the customer's concern.
2. Be empathetic.
3. Follow the company policy.
4. Do not promise actions that have not actually happened.
5. Do not invent refunds, investigations, or account changes.
6. Give clear next steps.
7. Keep the email concise.
8. Do not request passwords or OTPs.
9. Match the customer's emotional situation professionally.

Return only the response email.
"""

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt
    )

    return response.text.strip()