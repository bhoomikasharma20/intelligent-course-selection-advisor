import pandas as pd
import streamlit as st

import advisor as kb

st.set_page_config(page_title="Course Selection Advisor", page_icon="🎓", layout="wide")
st.title("🎓 Student Course Selection Advisor")
st.caption("Knowledge Representation and Reasoning project: rule-based expert system")

# ---------------- Sidebar: student profile ----------------
with st.sidebar:
    st.header("Student profile")
    choice = st.selectbox("Load a sample student", ["Custom"] + list(kb.STUDENTS))
    base = kb.STUDENTS.get(choice, {"completed": set(), "gpa": 3.0, "interest": "ai"})

    semester = st.radio("Semester", ["fall", "spring"], horizontal=True)
    gpa = st.slider("GPA", 0.0, 4.0, float(base["gpa"]), 0.1)
    interest = st.selectbox("Interest area", kb.AREAS, index=kb.AREAS.index(base["interest"]))
    completed = set(st.multiselect(
        "Completed courses",
        options=list(kb.COURSES),
        default=sorted(base["completed"]),
        format_func=lambda c: f"{c} - {kb.COURSES[c][0]}",
        key=f"completed_{choice}",
    ))

# ---------------- Reasoning ----------------
plan, used, limit = kb.recommend(completed, gpa, interest, semester)

c1, c2, c3 = st.columns(3)
c1.metric("Max credit hours (from GPA)", limit)
c2.metric("Recommended credits", used)
c3.metric("Courses completed", len(completed))

st.subheader("Recommended plan")
if plan:
    st.dataframe(pd.DataFrame(
        [{"Code": c, "Course": kb.COURSES[c][0], "Credits": kb.COURSES[c][1],
          "Area": kb.COURSES[c][2]} for c in plan]),
        hide_index=True, width="stretch")
else:
    st.info("No eligible courses for this semester.")

st.subheader("Why not the other courses? (explanation)")
rows = []
for code, (name, cr, area) in kb.COURSES.items():
    ok, reason = kb.course_status(completed, code, semester)
    if code in plan:
        continue
    if ok:
        reason = "Eligible, but skipped due to credit limit"
    rows.append({"Code": code, "Course": name, "Reason": reason})
st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

st.subheader("Prerequisite chain explorer")
target = st.selectbox("Pick a course", list(kb.COURSES),
                      format_func=lambda c: f"{c} - {kb.COURSES[c][0]}")
chain = sorted(kb.prereq_chain(target))
if chain:
    st.write(f"To take **{target}** you need (directly or indirectly):")
    for p in chain:
        mark = "✅" if p in completed else "❌"
        st.write(f"{mark} {p} - {kb.COURSES[p][0]}")
else:
    st.write("No prerequisites.")

with st.expander("Rules used by the system"):
    st.markdown("""
- **Max credits:** GPA ≥ 3.0 → 18, GPA ≥ 2.0 → 15, otherwise 12
- **Eligible(course)** = not completed AND offered this semester AND all prerequisites completed
- **Prerequisite chain** is computed recursively (prerequisites of prerequisites)
- **Priority:** courses matching the student's interest area come first
""")
