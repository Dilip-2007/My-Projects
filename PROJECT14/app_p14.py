import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
import requests


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Multi-Tool ReAct Agent",
    page_icon="🤖",
    layout="centered"
)


# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("🤖 Autonomous Multi-Tool ReAct Agent")

st.write(
    "Ask Gemini a compound question. "
    "The agent can use multiple tools sequentially."
)


# --------------------------------------------------
# Check API key
# --------------------------------------------------

if not api_key:
    st.error("GEMINI_API_KEY is missing from .env")
    st.stop()


# --------------------------------------------------
# Create Gemini client
# --------------------------------------------------

client = genai.Client(api_key=api_key)


# --------------------------------------------------
# Tool 1: Crypto price lookup
# --------------------------------------------------

def get_crypto_price(coin: str) -> float:
    """
    Get the current cryptocurrency price in USD.

    Args:
        coin: Cryptocurrency ID such as bitcoin or ethereum.

    Returns:
        Current cryptocurrency price in USD.
    """

    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {
        "ids": coin.lower(),
        "vs_currencies": "usd"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if coin.lower() not in data:
        raise ValueError(
            f"Cryptocurrency '{coin}' was not found."
        )

    return data[coin.lower()]["usd"]


# --------------------------------------------------
# Tool 2: ROI calculator
# --------------------------------------------------

def calculate_roi(
    investment: float,
    buy_price: float,
    current_price: float
) -> dict:
    """
    Calculate cryptocurrency profit and ROI.

    Args:
        investment: Amount invested.
        buy_price: Price at which the asset was purchased.
        current_price: Current asset price.

    Returns:
        Dictionary containing quantity, current value,
        profit and ROI percentage.
    """

    if buy_price <= 0:
        raise ValueError("Buy price must be greater than zero.")

    quantity = investment / buy_price

    current_value = quantity * current_price

    profit = current_value - investment

    roi_percentage = (profit / investment) * 100

    return {
        "quantity": quantity,
        "current_value": current_value,
        "profit": profit,
        "roi_percentage": roi_percentage
    }


# --------------------------------------------------
# Register tools
# --------------------------------------------------

tools = [
    get_crypto_price,
    calculate_roi
]


# --------------------------------------------------
# User input
# --------------------------------------------------

question = st.text_area(
    "💬 Ask your compound question:",
    placeholder=(
        "Example: "
        "If I invested $1000 in bitcoin at $50000, "
        "what is my profit at the current price?"
    )
)


# --------------------------------------------------
# Run Agent
# --------------------------------------------------

if st.button("🚀 Run Agent"):

    if question.strip() == "":
        st.warning("Please enter a question.")
        st.stop()

    st.subheader("🔎 Agent Trace")

    try:

        # ------------------------------------------
        # Initial prompt
        # ------------------------------------------

        messages = [
            {
                "role": "user",
                "parts": [
                    {
                        "text": question
                    }
                ]
            }
        ]


        # ------------------------------------------
        # ReAct loop
        # ------------------------------------------

        for step in range(5):

            with st.status(
                f"Step {step + 1}: Agent thinking...",
                expanded=True
            ) as status:

                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=messages,
                    config={
                        "tools": tools
                    }
                )

                candidate = response.candidates[0]

                function_calls = []

                for part in candidate.content.parts:

                    if part.function_call:
                        function_calls.append(
                            part.function_call
                        )

                # ----------------------------------
                # No tool call = final answer
                # ----------------------------------

                if not function_calls:

                    status.update(
                        label="✅ Final answer generated",
                        state="complete"
                    )

                    st.subheader("🎯 Final Answer")

                    st.write(response.text)

                    break


                # ----------------------------------
                # Add Gemini response to history
                # ----------------------------------

                messages.append(candidate.content)


                # ----------------------------------
                # Execute tools
                # ----------------------------------

                tool_parts = []

                for function_call in function_calls:

                    tool_name = function_call.name

                    tool_args = dict(
                        function_call.args
                    )

                    st.write(
                        f"🔧 Calling `{tool_name}`"
                    )

                    st.write(
                        f"Arguments: `{tool_args}`"
                    )


                    # Find the requested tool
                    selected_tool = None

                    for tool in tools:

                        if tool.__name__ == tool_name:
                            selected_tool = tool
                            break


                    if selected_tool is None:

                        result = {
                            "error":
                            f"Tool {tool_name} not found."
                        }

                    else:

                        try:

                            result = selected_tool(
                                **tool_args
                            )

                        except Exception as e:

                            result = {
                                "error": str(e)
                            }


                    st.write(
                        f"📦 Tool result: `{result}`"
                    )


                    # --------------------------------
                    # Send tool result back to Gemini
                    # --------------------------------

                    tool_parts.append(
                        {
                            "function_response": {
                                "name": tool_name,
                                "response": {
                                    "result": result
                                }
                            }
                        }
                    )


                messages.append(
                    {
                        "role": "user",
                        "parts": tool_parts
                    }
                )


                status.update(
                    label=f"✅ Step {step + 1} completed",
                    state="complete"
                )


        else:

            st.warning(
                "The agent reached the maximum "
                "5-step limit."
            )


    except Exception as e:

        st.error(
            f"Something went wrong: {e}"
        )