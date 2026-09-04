import streamlit as st
import sqlite3
import pandas as pd
import os
from google import genai

# -----------------------------
# Database setup
# -----------------------------
DB_NAME = "university.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                roll_no INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                course TEXT NOT NULL,
                marks REAL NOT NULL,
                grade TEXT NOT NULL
            )
        """)
        conn.commit()

    except sqlite3.Error as e:
        st.error(f"Database initialization error: {e}")

    finally:
        if conn:
            conn.close()


def calculate_grade(marks: float) -> str:
    if marks >= 90:
        return "A"
    elif marks >= 75:
        return "B"
    elif marks >= 60:
        return "C"
    else:
        return "D"


def insert_student(roll_no, name, department, course, marks, grade):
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO students
            (roll_no, name, department, course, marks, grade)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (roll_no, name, department, course, marks, grade),
        )

        conn.commit()
        return True, None

    except sqlite3.Error as e:
        return False, str(e)

    finally:
        if conn:
            conn.close()


def run_query(query: str):
    conn = None

    try:
        conn = get_connection()

        df = pd.read_sql_query(query, conn)

        return df, None

    except sqlite3.Error as e:
        return None, str(e)

    except pd.errors.DatabaseError as e:
        return None, str(e)

    finally:
        if conn:
            conn.close()


# -----------------------------
# Gemini Natural Language → SQL
# -----------------------------

def generate_sql_from_english(user_question):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None, "GEMINI_API_KEY is not set."

    try:

        client = genai.Client(api_key=api_key)

        prompt = f"""
You are an SQL generator for a university student database.

The SQLite database has exactly one table:

students

Columns:
- roll_no INTEGER
- name TEXT
- department TEXT
- course TEXT
- marks REAL
- grade TEXT

Valid departments are:
- Computer Science
- Data Science
- Electronics
- Mechanical

Grade rules:
- marks >= 90 → A
- marks >= 75 → B
- marks >= 60 → C
- marks < 60 → D

Convert the user's normal English question into ONE SQLite SELECT query.

IMPORTANT RULES:
1. Generate ONLY a SELECT or WITH query.
2. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, REPLACE, or other modifying SQL.
3. Do not use markdown.
4. Do not explain anything.
5. Return only the SQL query.
6. Use only the students table and its columns.

User question:
{user_question}
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        sql_query = response.text.strip()

        # Remove accidental markdown fences
        sql_query = sql_query.replace("```sql", "")
        sql_query = sql_query.replace("```", "")
        sql_query = sql_query.strip()

        # Safety check
        first_word = sql_query.split()[0].upper()

        if first_word not in ["SELECT", "WITH"]:
            return None, "Gemini generated a non-read-only query."

        return sql_query, None

    except Exception as e:
        return None, str(e)


# -----------------------------
# App configuration
# -----------------------------
st.set_page_config(
    page_title="Student Academic Records & Report Studio",
    layout="wide"
)

st.title("🎓 Student Academic Records & Report Studio")

init_db()

tab1, tab2 = st.tabs(
    ["🎓 Register Student", "📊 Academic Reports"]
)


# =====================================================
# TAB 1: Register Student
# =====================================================

with tab1:

    st.subheader("Register a New Student")

    with st.form(
        "registration_form",
        clear_on_submit=True
    ):

        roll_no = st.number_input(
            "Roll Number",
            min_value=1,
            step=1,
            format="%d"
        )

        name = st.text_input(
            "Full Name"
        )

        department = st.selectbox(
            "Department",
            [
                "Computer Science",
                "Data Science",
                "Electronics",
                "Mechanical"
            ]
        )

        course = st.text_input(
            "Course Name"
        )

        marks = st.number_input(
            "Marks",
            min_value=0.0,
            max_value=100.0,
            step=0.5
        )

        submitted = st.form_submit_button(
            "Register Student"
        )

        if submitted:

            if not name.strip() or not course.strip():

                st.warning(
                    "Please fill in all fields before submitting."
                )

            else:

                grade = calculate_grade(marks)

                success, error = insert_student(
                    int(roll_no),
                    name.strip(),
                    department,
                    course.strip(),
                    marks,
                    grade
                )

                if success:

                    st.success(
                        f"✅ Student '{name}' registered successfully "
                        f"with Grade '{grade}'!"
                    )

                else:

                    st.error(
                        f"❌ Could not register student. Error: {error}"
                    )


# =====================================================
# TAB 2: Academic Reports
# =====================================================

with tab2:

    st.subheader("Generate Academic Reports")

    report_options = {

        "All Students List":
            "SELECT * FROM students;",

        "Top Performers (>= 75 Marks)":
            (
                "SELECT name, department, marks, grade "
                "FROM students "
                "WHERE marks >= 75 "
                "ORDER BY marks DESC;"
            ),

        "Department-wise Average Marks":
            (
                "SELECT department, AVG(marks) AS avg_marks "
                "FROM students "
                "GROUP BY department;"
            ),

        "Grade Breakdown Count":
            (
                "SELECT grade, COUNT(*) AS total_students "
                "FROM students "
                "GROUP BY grade;"
            ),

        "Custom SQL Query":
            None,

        "🤖 Ask in Natural Language":
            None
    }


    selected_report = st.selectbox(
        "Select a Report",
        list(report_options.keys())
    )


    # =================================================
    # NORMAL CUSTOM SQL
    # =================================================

    if selected_report == "Custom SQL Query":

        query = st.text_area(
            "Enter your custom SQL query "
            "(SELECT statements recommended):",

            value="SELECT * FROM students;",

            height=120
        )

        user_question = None


    # =================================================
    # GEMINI NATURAL LANGUAGE
    # =================================================

    elif selected_report == "🤖 Ask in Natural Language":

        st.info(
            "Ask your question in normal English. "
            "Gemini will convert it into SQL."
        )

        user_question = st.text_area(
            "💬 Ask your question",

            placeholder=(
                "Example: Show me all students who scored above 80"
            ),

            height=100
        )

        query = None


    # =================================================
    # PREDEFINED REPORT
    # =================================================

    else:

        query = report_options[selected_report]

        user_question = None


    # =================================================
    # CHART CHECKBOX
    # =================================================

    generate_chart = st.checkbox(
        "Generate Chart Visualization"
    )


    # =================================================
    # RUN REPORT BUTTON
    # =================================================

    run_report = st.button(
        "Run Report",
        type="primary"
    )


    if run_report:

        # ---------------------------------------------
        # If Gemini Natural Language is selected
        # ---------------------------------------------

        if selected_report == "🤖 Ask in Natural Language":

            if not user_question or not user_question.strip():

                st.warning(
                    "Please enter your question."
                )

                st.stop()


            with st.spinner(
                "🤖 Gemini is converting your question into SQL..."
            ):

                query, gemini_error = generate_sql_from_english(
                    user_question
                )


            if gemini_error:

                st.error(
                    f"❌ Gemini error: {gemini_error}"
                )

                st.stop()


            st.success(
                "✅ Natural language converted to SQL successfully!"
            )


        # ---------------------------------------------
        # Display SQL
        # ---------------------------------------------

        st.subheader("Executed SQL Query")

        st.code(
            query,
            language="sql"
        )


        # ---------------------------------------------
        # Execute SQL
        # ---------------------------------------------

        df, error = run_query(query)


        if error:

            st.error(
                f"❌ Query failed: {error}"
            )


        elif df is None or df.empty:

            st.info(
                "No data returned for this query."
            )


        else:

            # -----------------------------------------
            # Display result table
            # -----------------------------------------

            st.subheader("📋 Report Results")

            st.dataframe(
                df,
                use_container_width=True
            )


            # -----------------------------------------
            # Generate chart
            # -----------------------------------------

            if generate_chart:

                numeric_cols = (
                    df.select_dtypes(
                        include="number"
                    ).columns.tolist()
                )


                if not numeric_cols:

                    st.warning(
                        "No numeric columns available to chart."
                    )


                else:

                    # Find label column
                    label_cols = [
                        c for c in df.columns
                        if c not in numeric_cols
                    ]


                    chart_df = df.copy()


                    if label_cols:

                        chart_df = chart_df.set_index(
                            label_cols[0]
                        )


                    st.subheader(
                        "📊 Chart Visualization"
                    )


                    st.bar_chart(
                        chart_df[numeric_cols]
                    )