import streamlit as st
from google import genai
from dotenv import load_dotenv
import os


# --------------------------------
# Load environment variables
# --------------------------------
load_dotenv()


# --------------------------------
# Page configuration
# --------------------------------
st.set_page_config(
    page_title="Autonomous Function Calling Agent",
    page_icon="🤖",
    layout="centered"
)


# --------------------------------
# Get API key
# --------------------------------
api_key = os.getenv("GEMINI_API_KEY")


if not api_key:

    st.error(
        "GEMINI_API_KEY is missing. "
        "Please check your .env file."
    )

    st.stop()


# --------------------------------
# Create Gemini client
# --------------------------------
client = genai.Client(
    api_key=api_key
)


# ==================================================
# PYTHON FUNCTIONS / TOOLS
# ==================================================


# --------------------------------
# Loan EMI Calculator
# --------------------------------
def calculate_emi(
    principal: float,
    annual_interest_rate: float,
    tenure_years: int
) -> dict:
    """
    Calculate monthly EMI for a loan.

    Args:
        principal: Loan amount in rupees.
        annual_interest_rate: Annual interest rate in percentage.
        tenure_years: Loan tenure in years.

    Returns:
        Dictionary containing EMI, total payment and total interest.
    """

    monthly_rate = (
        annual_interest_rate / 100 / 12
    )

    number_of_months = (
        tenure_years * 12
    )

    if monthly_rate == 0:

        emi = (
            principal / number_of_months
        )

    else:

        emi = (
            principal
            * monthly_rate
            * (1 + monthly_rate) ** number_of_months
            / (
                (1 + monthly_rate) ** number_of_months - 1
            )
        )

    total_payment = (
        emi * number_of_months
    )

    total_interest = (
        total_payment - principal
    )

    return {
        "loan_amount": round(principal, 2),
        "monthly_emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2)
    }


# --------------------------------
# Stock Metric Calculator
# --------------------------------
def calculate_stock_metrics(
    price: float,
    earnings_per_share: float,
    dividend_per_share: float
) -> dict:
    """
    Calculate basic stock valuation metrics.

    Args:
        price: Current stock price.
        earnings_per_share: Earnings per share.
        dividend_per_share: Dividend per share.

    Returns:
        Dictionary containing P/E ratio and dividend yield.
    """

    if earnings_per_share > 0:

        pe_ratio = (
            price / earnings_per_share
        )

    else:

        pe_ratio = None


    if price > 0:

        dividend_yield = (
            dividend_per_share
            / price
            * 100
        )

    else:

        dividend_yield = 0


    return {
        "price": round(price, 2),
        "eps": round(earnings_per_share, 2),
        "pe_ratio": (
            round(pe_ratio, 2)
            if pe_ratio is not None
            else None
        ),
        "dividend_yield_percent": round(
            dividend_yield,
            2
        )
    }


# ==================================================
# TOOL DECLARATIONS
# ==================================================

emi_tool = {
    "name": "calculate_emi",
    "description": (
        "Calculate the monthly EMI, total payment, "
        "and total interest for a loan."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "principal": {
                "type": "number",
                "description": "Loan amount in rupees."
            },
            "annual_interest_rate": {
                "type": "number",
                "description": "Annual interest rate in percentage."
            },
            "tenure_years": {
                "type": "integer",
                "description": "Loan tenure in years."
            }
        },
        "required": [
            "principal",
            "annual_interest_rate",
            "tenure_years"
        ]
    }
}


stock_tool = {
    "name": "calculate_stock_metrics",
    "description": (
        "Calculate basic stock metrics including "
        "P/E ratio and dividend yield."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "price": {
                "type": "number",
                "description": "Current stock price."
            },
            "earnings_per_share": {
                "type": "number",
                "description": "Earnings per share."
            },
            "dividend_per_share": {
                "type": "number",
                "description": "Dividend per share."
            }
        },
        "required": [
            "price",
            "earnings_per_share",
            "dividend_per_share"
        ]
    }
}


tools = [
    {
        "function_declarations": [
            emi_tool,
            stock_tool
        ]
    }
]


# ==================================================
# STREAMLIT UI
# ==================================================

st.title(
    "🤖 Autonomous Function Calling Agent"
)

st.write(
    "Ask Gemini a question. Gemini can decide "
    "when to call a Python function to calculate "
    "the answer."
)


question = st.text_area(
    "💬 Ask your question:",
    placeholder=(
        "Example: Calculate EMI for a ₹5,00,000 "
        "loan at 10% interest for 5 years."
    )
)


# --------------------------------
# Run Agent
# --------------------------------
if st.button("🚀 Ask Agent"):

    if question.strip() == "":

        st.warning(
            "Please enter a question."
        )

    else:

        try:

            # --------------------------------
            # First Gemini request
            # --------------------------------
            with st.spinner(
                "Gemini is deciding which tool to use..."
            ):

                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=question,
                    config={
                        "tools": tools
                    }
                )


            # --------------------------------
            # Check whether Gemini requested
            # a function call
            # --------------------------------
            function_call_found = False


            for part in response.candidates[0].content.parts:

                if hasattr(part, "function_call"):

                    function_call = part.function_call

                    if function_call:

                        function_call_found = True

                        function_name = (
                            function_call.name
                        )

                        function_args = dict(
                            function_call.args
                        )


                        # --------------------------------
                        # Display selected tool
                        # --------------------------------
                        st.info(
                            f"🔧 Gemini selected tool: "
                            f"`{function_name}`"
                        )


                        # --------------------------------
                        # Execute EMI function
                        # --------------------------------
                        if function_name == "calculate_emi":

                            result = calculate_emi(
                                **function_args
                            )


                        # --------------------------------
                        # Execute stock function
                        # --------------------------------
                        elif function_name == "calculate_stock_metrics":

                            result = calculate_stock_metrics(
                                **function_args
                            )


                        else:

                            result = {
                                "error": "Unknown function."
                            }


                        # --------------------------------
                        # Show function result
                        # --------------------------------
                        st.write(
                            "🔢 Python function result:"
                        )

                        st.json(result)


                        # --------------------------------
                        # Send result back to Gemini
                        # --------------------------------
                        with st.spinner(
                            "Gemini is preparing the final answer..."
                        ):

                            final_response = (
                                client.models.generate_content(
                                    model="gemini-3.7-flash",
                                    contents=[
                                        question,
                                        response.candidates[
                                            0
                                        ].content,
                                        {
                                            "function_response": {
                                                "name": function_name,
                                                "response": result
                                            }
                                        }
                                    ],
                                    config={
                                        "tools": tools
                                    }
                                )
                            )


                        # --------------------------------
                        # Display final answer
                        # --------------------------------
                        st.subheader(
                            "🤖 Agent Response"
                        )

                        st.write(
                            final_response.text
                        )


            # --------------------------------
            # No function required
            # --------------------------------
            if not function_call_found:

                st.subheader(
                    "🤖 Agent Response"
                )

                st.write(
                    response.text
                )


        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )