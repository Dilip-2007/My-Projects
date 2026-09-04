import streamlit as st
import json
import os


# --------------------------------
# Page configuration
# --------------------------------
st.set_page_config(
    page_title="Quiz Master",
    page_icon="🧠",
    layout="centered"
)


# --------------------------------
# File configuration
# --------------------------------
LEADERBOARD_FILE = "leaderboard.json"


# --------------------------------
# Quiz questions
# --------------------------------
questions = [
    {
        "question": "What does AI stand for?",
        "options": [
            "Artificial Intelligence",
            "Automated Internet",
            "Advanced Information",
            "Artificial Internet"
        ],
        "answer": "Artificial Intelligence"
    },

    {
        "question": "Which language are we using to build this app?",
        "options": [
            "Java",
            "Python",
            "C++",
            "HTML"
        ],
        "answer": "Python"
    },

    {
        "question": "Which library are we using to create the web UI?",
        "options": [
            "NumPy",
            "Pandas",
            "Streamlit",
            "TensorFlow"
        ],
        "answer": "Streamlit"
    },

    {
        "question": "What does API stand for?",
        "options": [
            "Application Programming Interface",
            "Advanced Programming Internet",
            "Application Process Integration",
            "Automated Program Interface"
        ],
        "answer": "Application Programming Interface"
    },

    {
        "question": "Which file format are we using to store the leaderboard?",
        "options": [
            "TXT",
            "JSON",
            "PNG",
            "HTML"
        ],
        "answer": "JSON"
    }
]


# --------------------------------
# Load leaderboard
# --------------------------------
def load_leaderboard():

    if not os.path.exists(LEADERBOARD_FILE):
        return []

    try:
        with open(LEADERBOARD_FILE, "r") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


# --------------------------------
# Save leaderboard
# --------------------------------
def save_leaderboard(leaderboard):

    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(leaderboard, file, indent=4)


# --------------------------------
# Initialize session state
# --------------------------------
if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "quiz_finished" not in st.session_state:
    st.session_state.quiz_finished = False

if "player_name" not in st.session_state:
    st.session_state.player_name = ""

if "answered" not in st.session_state:
    st.session_state.answered = False


# --------------------------------
# Title
# --------------------------------
st.title("🧠 Quiz Master")

st.write(
    "Test your AI and Python knowledge and compete on the leaderboard!"
)


# --------------------------------
# Player name
# --------------------------------
if not st.session_state.player_name:

    name = st.text_input(
        "Enter your name:",
        placeholder="Example: Alex"
    )

    if st.button("Start Quiz"):

        if name.strip() == "":
            st.warning("Please enter your name.")

        else:
            st.session_state.player_name = name.strip()
            st.rerun()


# --------------------------------
# Quiz
# --------------------------------
elif not st.session_state.quiz_finished:

    question_number = st.session_state.current_question

    question_data = questions[question_number]

    st.write(
        f"### Question {question_number + 1} of {len(questions)}"
    )

    st.write(question_data["question"])

    selected_answer = st.radio(
        "Choose your answer:",
        question_data["options"],
        key=f"question_{question_number}"
    )

    if st.button("Submit Answer"):

        if selected_answer == question_data["answer"]:

            st.success("Correct! ✅")
            st.session_state.score += 1

        else:

            st.error(
                f"Wrong ❌ The correct answer is: "
                f"{question_data['answer']}"
            )

        st.session_state.answered = True


    # --------------------------------
    # Next question
    # --------------------------------
    if st.session_state.answered:

        if question_number < len(questions) - 1:

            if st.button("Next Question"):

                st.session_state.current_question += 1
                st.session_state.answered = False

                st.rerun()

        else:

            if st.button("Finish Quiz"):

                leaderboard = load_leaderboard()

                result = {
                    "name": st.session_state.player_name,
                    "score": st.session_state.score,
                    "total": len(questions)
                }

                leaderboard.append(result)

                leaderboard.sort(
                    key=lambda x: x["score"],
                    reverse=True
                )

                save_leaderboard(leaderboard)

                st.session_state.quiz_finished = True

                st.rerun()


# --------------------------------
# Final result
# --------------------------------
else:

    st.success("🎉 Quiz completed!")

    st.subheader(
        f"Congratulations, {st.session_state.player_name}!"
    )

    st.write(
        f"Your score: "
        f"**{st.session_state.score}/{len(questions)}**"
    )

    st.divider()

    st.subheader("🏆 Leaderboard")

    leaderboard = load_leaderboard()

    if leaderboard:

        for index, player in enumerate(leaderboard, start=1):

            st.write(
                f"**{index}. {player['name']}** — "
                f"{player['score']}/{player['total']}"
            )

    else:

        st.write("No scores yet.")

    st.divider()

    if st.button("Play Again"):

        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.quiz_finished = False
        st.session_state.player_name = ""
        st.session_state.answered = False

        st.rerun()