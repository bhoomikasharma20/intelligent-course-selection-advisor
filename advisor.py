"""
Student Course Selection Advisor - KRR logic (Python version)

Knowledge base  : COURSES, PREREQ, OFFERED (facts)
Rules           : max_credits, missing_prereqs, course_status, recommend
Recursive rule  : prereq_chain (transitive prerequisites)
Explanation     : course_status returns the reason for every decision
"""

# ---------------- Knowledge Base (Facts) ----------------

# code: (name, credit_hours, area)
COURSES = {
    "cs101": ("Programming Fundamentals", 3, "programming"),
    "cs102": ("Object Oriented Programming", 3, "programming"),
    "ma101": ("Discrete Mathematics", 3, "math"),
    "cs201": ("Data Structures", 3, "programming"),
    "ma201": ("Probability and Statistics", 3, "math"),
    "cs202": ("Database Systems", 3, "data"),
    "cs301": ("Artificial Intelligence", 3, "ai"),
    "cs302": ("Knowledge Representation and Reasoning", 3, "ai"),
    "cs303": ("Machine Learning", 3, "ai"),
    "cs304": ("Web Engineering", 3, "web"),
    "cs401": ("Final Year Project I", 3, "project"),
}

PREREQ = {
    "cs102": ["cs101"],
    "cs201": ["cs102", "ma101"],
    "cs202": ["cs201"],
    "cs301": ["cs201"],
    "cs302": ["cs301", "ma101"],
    "cs303": ["cs301", "ma201"],
    "cs304": ["cs202"],
    "cs401": ["cs302"],
}

OFFERED = {
    "cs101": {"fall", "spring"},
    "cs102": {"fall", "spring"},
    "ma101": {"fall"},
    "cs201": {"fall", "spring"},
    "ma201": {"spring"},
    "cs202": {"spring"},
    "cs301": {"fall"},
    "cs302": {"fall"},
    "cs303": {"spring"},
    "cs304": {"fall"},
    "cs401": {"fall"},
}

STUDENTS = {
    "ali": {"completed": {"cs101", "cs102", "ma101", "cs201", "ma201"},
            "gpa": 3.2, "interest": "ai"},
    "sara": {"completed": {"cs101"}, "gpa": 2.4, "interest": "web"},
}

AREAS = sorted({a for _, _, a in COURSES.values()})


# ---------------- Rules ----------------

def max_credits(gpa):
    """GPA >= 3.0 -> 18, GPA >= 2.0 -> 15, otherwise 12."""
    if gpa >= 3.0:
        return 18
    if gpa >= 2.0:
        return 15
    return 12


def missing_prereqs(completed, code):
    return [p for p in PREREQ.get(code, []) if p not in completed]


def course_status(completed, code, semester):
    """Return (is_eligible, reason)."""
    if code in completed:
        return False, "Already completed"
    if semester not in OFFERED[code]:
        return False, f"Not offered in {semester} semester"
    missing = missing_prereqs(completed, code)
    if missing:
        return False, "Missing prerequisite(s): " + ", ".join(missing)
    return True, "All conditions satisfied"


def eligible_courses(completed, semester):
    return [c for c in COURSES if course_status(completed, c, semester)[0]]


def prereq_chain(code):
    """Recursive rule: all direct and indirect prerequisites of a course."""
    result = set()
    for p in PREREQ.get(code, []):
        result.add(p)
        result |= prereq_chain(p)
    return result


def recommend(completed, gpa, interest, semester):
    """Eligible courses, interest area first, greedy within credit limit."""
    limit = max_credits(gpa)
    eligible = eligible_courses(completed, semester)
    eligible.sort(key=lambda c: (COURSES[c][2] != interest, c))
    plan, used = [], 0
    for c in eligible:
        cr = COURSES[c][1]
        if used + cr <= limit:
            plan.append(c)
            used += cr
    return plan, used, limit


if __name__ == "__main__":
    for name, s in STUDENTS.items():
        plan, used, limit = recommend(s["completed"], s["gpa"], s["interest"], "fall")
        print(f"{name}: plan={plan} credits={used}/{limit}")
    print("cs401 chain:", sorted(prereq_chain("cs401")))
