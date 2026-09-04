import io
import traceback
from contextlib import redirect_stdout, redirect_stderr


# Hidden tests for each challenge
HIDDEN_TESTS = {

    "A": """
assert process_transactions([]) == {
    "net_total": 0.0,
    "valid_count": 0
}

assert process_transactions([
    {"amount": "$15.50"},
    {"amount": -5.0},
    {"amount": None}
]) == {
    "net_total": 10.5,
    "valid_count": 2
}
""",

    "B": """
assert spiral_order([]) == []

assert spiral_order([[1, 2, 3]]) == [1, 2, 3]

assert spiral_order([[1], [2], [3]]) == [1, 2, 3]
""",

    "C": """
assert calc_weighted_avg([], []) == 0.0

assert calc_weighted_avg([80, 90], [0, 0]) == 0.0

assert calc_weighted_avg([100], [5]) == 100.0
""",

    "D": """
assert count_error_hours([]) == {}

assert count_error_hours([
    "2026-09-01 14:10:00 - INFO - OK",
    "corrupted_log_entry"
]) == {}

assert count_error_hours([
    "2026-09-01 14:10:00 - ERROR - Failed",
    "2026-09-01 14:25:00 - ERROR - Failed again",
    "2026-09-01 15:30:00 - ERROR - Database error"
]) == {
    "14": 2,
    "15": 1
}
"""
}


def run_code(code, challenge):
    """
    Execute generated Python code and hidden tests.
    Returns success status, output and traceback.
    """

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    namespace = {}

    try:

        # Execute generated code
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code, namespace)

            # Execute hidden tests
            test_code = HIDDEN_TESTS[challenge]
            exec(test_code, namespace)

        return {
            "success": True,
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
            "error": None
        }

    except Exception:
        error = traceback.format_exc()

        return {
            "success": False,
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
            "error": error
        }