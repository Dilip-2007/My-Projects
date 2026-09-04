from google import genai
from config import API_KEY, DEFAULT_MODEL


# Create Gemini client
if not API_KEY:
    raise ValueError(
        "Gemini API key not found. "
        "Set the GEMINI_API_KEY environment variable."
    )

client = genai.Client(api_key=API_KEY)


def clean_code(text):
    """
    Remove Markdown code fences from Gemini response.
    """

    text = text.strip()

    if text.startswith("```python"):
        text = text[len("```python"):]

    elif text.startswith("```"):
        text = text[len("```"):]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def generate_code(prompt):
    """
    Ask Gemini to generate the initial Python solution.
    """

    system_prompt = f"""
You are an expert Python programmer.

The user wants the following function:

{prompt}

Generate a complete Python implementation.

Requirements:
- Return ONLY Python code.
- Do NOT use Markdown.
- Do NOT use ``` fences.
- Include the required function definition.
- Handle edge cases carefully.
- Do not explain the code.
"""

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=system_prompt
    )

    return clean_code(response.text)


def repair_code(prompt, code, error):
    """
    Send failed code and traceback back to Gemini
    for automatic repair.
    """

    repair_prompt = f"""
You are a self-healing Python coding agent.

USER REQUIREMENT:
{prompt}

CURRENT BROKEN CODE:
{code}

TEST/RUNTIME ERROR:
{error}

Your task is to repair the Python code.

Rules:
1. Fix the actual problem shown by the error.
2. Preserve the required function name.
3. Handle edge cases.
4. Return the COMPLETE corrected Python program.
5. Return ONLY Python code.
6. Do NOT use Markdown.
7. Do NOT include ```python.
8. Do NOT explain anything.

Generate the corrected code now.
"""

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=repair_prompt
    )

    return clean_code(response.text)