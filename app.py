import streamlit as st

from parser import parse_resume
from search import search_resumes


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="HireSense",
    page_icon="🔎",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 25px;
    }

    .candidate-name {
        font-size: 23px;
        font-weight: 600;
    }

    .score {
        font-size: 36px;
        font-weight: 700;
    }

    .section-title {
        font-size: 20px;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🔎 HireSense</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Intelligent Resume Screening & Candidate Search'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "Upload resumes, extract structured candidate profiles, "
    "and find the best candidates using intelligent matching."
)


# ============================================================
# SESSION STATE
# ============================================================

if "resumes" not in st.session_state:
    st.session_state.resumes = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📄 Resume Processing")

    uploaded_files = st.file_uploader(
        "Upload PDF resumes",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload up to 10 PDF resumes."
    )

    if uploaded_files:

        if len(uploaded_files) > 10:

            st.error(
                "Please upload a maximum of 10 resumes."
            )

        else:

            st.info(
                f"{len(uploaded_files)} resume(s) selected."
            )

            if st.button(
                "🚀 Process Resumes",
                type="primary",
                use_container_width=True
            ):

                st.session_state.resumes = []

                progress = st.progress(0)

                status = st.empty()

                for i, file in enumerate(uploaded_files):

                    status.write(
                        f"Processing `{file.name}`..."
                    )

                    try:

                        resume = parse_resume(file)

                        resume["filename"] = file.name

                        st.session_state.resumes.append(
                            resume
                        )

                    except Exception as e:

                        st.error(
                            f"Could not process "
                            f"{file.name}: {e}"
                        )

                    progress.progress(
                        (i + 1) / len(uploaded_files)
                    )

                status.success(
                    f"Processed "
                    f"{len(st.session_state.resumes)} "
                    f"resume(s)."
                )


# ============================================================
# DATA
# ============================================================

resumes = st.session_state.resumes


# ============================================================
# DASHBOARD METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "📄 Resumes",
        len(resumes)
    )


with col2:

    st.metric(
        "👤 Candidates",
        len(resumes)
    )


with col3:

    all_skills = set()

    for resume in resumes:

        all_skills.update(
            resume.get("skills", [])
        )

    st.metric(
        "🛠️ Skills Detected",
        len(all_skills)
    )


with col4:

    total_experience = sum(
        float(resume.get("experience", 0))
        for resume in resumes
    )

    avg_experience = (
        total_experience / len(resumes)
        if resumes
        else 0
    )

    st.metric(
        "💼 Avg Experience",
        f"{avg_experience:.1f} yrs"
    )


st.divider()


# ============================================================
# SEARCH SECTION
# ============================================================

st.subheader("🎯 Intelligent Candidate Search")

query = st.text_area(
    "Describe the candidate you're looking for",
    placeholder=(
        "Example: Python developers with 3+ years "
        "of machine learning experience and SQL skills"
    ),
    height=100
)


if query:

    if not resumes:

        st.info(
            "📄 Upload and process resumes first."
        )

    else:

        with st.spinner(
            "🔎 Analyzing candidates..."
        ):

            results = search_resumes(
                resumes,
                query
            )

        st.success(
            f"Found and ranked {len(results)} candidates."
        )

        st.divider()


        # ====================================================
        # RESULTS
        # ====================================================

        for index, resume in enumerate(results):

            score = resume.get(
                "score",
                0
            )

            breakdown = resume.get(
                "score_breakdown",
                {}
            )

            matched_skills = resume.get(
                "matched_skills",
                []
            )

            missing_skills = resume.get(
                "missing_skills",
                []
            )


            # Badge
            if score >= 80:

                badge = "🟢 Excellent Match"

            elif score >= 60:

                badge = "🟡 Good Match"

            else:

                badge = "⚪ Partial Match"


            # =================================================
            # CANDIDATE CARD
            # =================================================

            with st.container(border=True):

                left, right = st.columns(
                    [4, 1]
                )


                # ---------------------------------------------
                # LEFT SIDE
                # ---------------------------------------------

                with left:

                    st.markdown(
                        f'<div class="candidate-name">'
                        f'{"🥇" if index == 0 else "🥈" if index == 1 else "🥉" if index == 2 else "👤"} '
                        f'{index + 1}. '
                        f'{resume.get("name", "Unknown Candidate")}'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    st.write(
                        badge
                    )

                    st.write(
                        f"📧 "
                        f"{resume.get('email', 'Not found')}"
                    )

                    st.write(
                        f"📱 "
                        f"{resume.get('phone', 'Not found')}"
                    )

                    st.write(
                        f"💼 Experience: "
                        f"{resume.get('experience', 0)} years"
                    )


                    # Skills

                    skills = resume.get(
                        "skills",
                        []
                    )

                    if skills:

                        st.write(
                            "🛠️ **Skills:** "
                            + ", ".join(skills)
                        )


                    # Matched skills

                    if matched_skills:

                        st.success(
                            "✓ **Matched Skills:** "
                            + ", ".join(
                                matched_skills
                            )
                        )


                    # Missing skills

                    if missing_skills:

                        st.warning(
                            "⚠ **Missing Skills:** "
                            + ", ".join(
                                missing_skills
                            )
                        )


                    # Source

                    st.caption(
                        "📄 Source: "
                        + resume.get(
                            "filename",
                            "Unknown"
                        )
                    )


                # ---------------------------------------------
                # RIGHT SIDE
                # ---------------------------------------------

                with right:

                    st.metric(
                        "Suitability",
                        f"{score}%"
                    )

                    st.progress(
                        min(score / 100, 1.0)
                    )


                # =================================================
                # SCORE BREAKDOWN
                # =================================================

                st.markdown(
                    "#### 📊 Match Breakdown"
                )

                b1, b2, b3, b4 = st.columns(4)


                with b1:

                    value = breakdown.get(
                        "Skills",
                        0
                    )

                    st.metric(
                        "🛠️ Skills",
                        f"{value}/100"
                    )

                    st.progress(
                        min(value / 100, 1.0)
                    )


                with b2:

                    value = breakdown.get(
                        "Experience",
                        0
                    )

                    st.metric(
                        "💼 Experience",
                        f"{value}/100"
                    )

                    st.progress(
                        min(value / 100, 1.0)
                    )


                with b3:

                    value = breakdown.get(
                        "Education",
                        0
                    )

                    st.metric(
                        "🎓 Education",
                        f"{value}/100"
                    )

                    st.progress(
                        min(value / 100, 1.0)
                    )


                with b4:

                    value = breakdown.get(
                        "Relevance",
                        0
                    )

                    st.metric(
                        "🎯 Relevance",
                        f"{value}/100"
                    )

                    st.progress(
                        min(value / 100, 1.0)
                    )


                # =================================================
                # WHY THIS CANDIDATE
                # =================================================

                st.markdown(
                    "#### 💡 Why this candidate?"
                )

                reasons = []

                if matched_skills:

                    reasons.append(
                        f"Matches {len(matched_skills)} "
                        f"required skill(s): "
                        f"{', '.join(matched_skills)}"
                    )

                experience = float(
                    resume.get(
                        "experience",
                        0
                    )
                )

                if experience > 0:

                    reasons.append(
                        f"Has {experience:g} years "
                        f"of professional experience"
                    )

                if breakdown.get(
                    "Relevance",
                    0
                ) >= 60:

                    reasons.append(
                        "Resume content is highly "
                        "relevant to the search"
                    )

                if reasons:

                    for reason in reasons:

                        st.write(
                            "• " + reason
                        )

                else:

                    st.write(
                        "Limited matching information found."
                    )


# ============================================================
# BROWSE ALL RESUMES
# ============================================================

if resumes and not query:

    st.subheader(
        "📋 Processed Candidates"
    )

    for resume in resumes:

        name = resume.get(
            "name",
            "Unknown Candidate"
        )

        filename = resume.get(
            "filename",
            "Unknown file"
        )

        with st.expander(
            f"👤 {name} — {filename}"
        ):

            col1, col2 = st.columns(2)


            with col1:

                st.write(
                    "**Email:**",
                    resume.get(
                        "email",
                        "Not found"
                    )
                )

                st.write(
                    "**Phone:**",
                    resume.get(
                        "phone",
                        "Not found"
                    )
                )

                st.write(
                    "**Experience:**",
                    f"{resume.get('experience', 0)} years"
                )


            with col2:

                skills = resume.get(
                    "skills",
                    []
                )

                st.write(
                    "**Skills:**",
                    ", ".join(skills)
                    if skills
                    else "None detected"
                )

                st.write(
                    "**Education:**"
                )

                education = resume.get(
                    "education",
                    []
                )

                if education:

                    for item in education:

                        st.write(
                            f"- {item}"
                        )

                else:

                    st.write(
                        "Not detected"
                    )


# ============================================================
# EMPTY STATE
# ============================================================

if not resumes:

    st.info(
        "👈 Upload PDF resumes from the sidebar "
        "to get started."
    )
