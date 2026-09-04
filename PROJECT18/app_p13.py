import streamlit as st

from coder_agent import generate_code, repair_code
from sandbox import run_code


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Test-Driven Self-Healing AI Coder",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🤖 Test-Driven Self-Healing AI Coder")

st.write(
    "Autonomous TDD agent that generates Python code, "
    "runs hidden tests, detects failures and automatically repairs the code."
)


# --------------------------------------------------
# CHALLENGE INFORMATION
# --------------------------------------------------

CHALLENGES = {

    "Challenge A - Nested Transaction Aggregator": {
        "id": "A",
        "prompt": """
Write a Python function process_transactions(data) that takes
a list of transaction dictionaries and returns a dictionary:

{
    "net_total": float,
    "valid_count": int
}

The function should:
- Accept numeric amounts.
- Accept currency strings such as "$15.50".
- Ignore invalid or None amounts.
- Calculate the total of valid transactions.
- Count valid transactions.
- Return 0.0 and 0 for an empty list.
"""
    },

    "Challenge B - Clockwise Matrix Spiral": {
        "id": "B",
        "prompt": """
Write a Python function spiral_order(matrix) that returns
all elements of an N x M matrix in clockwise spiral order.

The function must correctly handle:
- Empty matrix
- Single row
- Single column
- Rectangular matrices
- Square matrices
"""
    },

    "Challenge C - Safe Weighted Average": {
        "id": "C",
        "prompt": """
Write a Python function calc_weighted_avg(scores, weights)
that returns the weighted average as a float rounded to
2 decimal places.

The function should:
- Handle empty lists.
- Handle zero total weight safely.
- Return 0.0 when total weight is zero.
- Correctly handle a single item.
"""
    },

    "Challenge D - Log Timestamp Frequency Counter": {
        "id": "D",
        "prompt": """
Write a Python function count_error_hours(logs) that takes
a list of log strings and returns a dictionary counting
ERROR log frequencies by hour.

Example:

[
    "2026-09-01 14:10:00 - ERROR - Failed",
    "2026-09-01 14:20:00 - ERROR - Failed again",
    "2026-09-01 15:30:00 - ERROR - Database error"
]

should produce:

{
    "14": 2,
    "15": 1
}

Ignore corrupted log entries and non-error entries.
Return an empty dictionary when there are no valid errors.
"""
    }
}


# --------------------------------------------------
# CHALLENGE SELECTION
# --------------------------------------------------

selected_challenge = st.selectbox(
    "Choose Challenge",
    list(CHALLENGES.keys())
)

challenge = CHALLENGES[selected_challenge]

st.subheader("Challenge Requirement")

st.info(challenge["prompt"])


# --------------------------------------------------
# OPTIONAL CUSTOM PROMPT
# --------------------------------------------------

use_custom = st.checkbox("Use my own prompt instead")

if use_custom:

    user_prompt = st.text_area(
        "Enter your Python function requirement",
        height=150,
        placeholder="Example: Write a function that checks whether a number is prime."
    )

else:

    user_prompt = challenge["prompt"]


# --------------------------------------------------
# RUN BUTTON
# --------------------------------------------------

if st.button("🚀 Generate & Test", type="primary"):

    if not user_prompt.strip():

        st.error("Please enter a requirement.")

    else:

        # Store current code
        code = None

        # Maximum attempts
        max_attempts = 3

        # Track success
        success = False

        # --------------------------------------------------
        # ATTEMPT LOOP
        # --------------------------------------------------

        for attempt in range(1, max_attempts + 1):

            st.divider()

            st.subheader(f"🔄 Attempt {attempt} of {max_attempts}")

            # --------------------------------------------------
            # GENERATION
            # --------------------------------------------------

            if attempt == 1:

                with st.status(
                    "Generating Python code with Gemini...",
                    expanded=True
                ) as status:

                    try:

                        code = generate_code(user_prompt)

                        st.write("✅ Code generated.")

                        status.update(
                            label="Code generation completed",
                            state="complete"
                        )

                    except Exception as e:

                        status.update(
                            label="Gemini generation failed",
                            state="error"
                        )

                        st.error(str(e))

                        break

            else:

                with st.status(
                    "Repairing code using Gemini...",
                    expanded=True
                ) as status:

                    try:

                        code = repair_code(
                            user_prompt,
                            code,
                            error
                        )

                        st.write("🔧 Gemini generated repaired code.")

                        status.update(
                            label="Repair completed",
                            state="complete"
                        )

                    except Exception as e:

                        status.update(
                            label="Repair failed",
                            state="error"
                        )

                        st.error(str(e))

                        break


            # --------------------------------------------------
            # SHOW GENERATED CODE
            # --------------------------------------------------

            st.write("### Generated Code")

            st.code(code, language="python")


            # --------------------------------------------------
            # RUN HIDDEN TESTS
            # --------------------------------------------------

            with st.status(
                "Running hidden tests...",
                expanded=True
            ) as test_status:

                result = run_code(
                    code,
                    challenge["id"]
                )

                if result["success"]:

                    test_status.update(
                        label="All hidden tests passed!",
                        state="complete"
                    )

                    st.success(
                        "🎉 All hidden tests passed successfully!"
                    )

                    success = True

                    break

                else:

                    test_status.update(
                        label="Hidden test failed",
                        state="error"
                    )

                    st.error("❌ Hidden test failure detected.")

                    error = result["error"]

                    st.write("### Traceback / Error")

                    st.code(
                        error,
                        language="text"
                    )

                    if result["stdout"]:

                        st.write("### Program Output")

                        st.code(
                            result["stdout"],
                            language="text"
                        )


                    # --------------------------------------------------
                    # REPAIR MESSAGE
                    # --------------------------------------------------

                    if attempt < max_attempts:

                        st.warning(
                            "⚠️ Sending the failure information "
                            "back to Gemini for automatic repair..."
                        )

                    else:

                        st.error(
                            "❌ Maximum repair attempts reached."
                        )


        # --------------------------------------------------
        # FINAL RESULT
        # --------------------------------------------------

        st.divider()

        if success:

            st.header("✅ Final Verified Code")

            st.success(
                f"Solution verified successfully in {attempt} attempt(s)."
            )

            st.code(
                code,
                language="python"
            )

        else:

            st.header("❌ Verification Failed")

            st.warning(
                "The agent could not make all hidden tests pass "
                "within 3 attempts."
            )