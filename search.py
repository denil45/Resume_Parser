import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# SKILL ALIASES
# ============================================================

SKILL_ALIASES = {

    "python": [
        "python"
    ],

    "machine learning": [
        "machine learning",
        "ml"
    ],

    "deep learning": [
        "deep learning",
        "dl"
    ],

    "natural language processing": [
        "natural language processing",
        "nlp"
    ],

    "computer vision": [
        "computer vision",
        "cv"
    ],

    "sql": [
        "sql"
    ],

    "tensorflow": [
        "tensorflow"
    ],

    "pytorch": [
        "pytorch"
    ],

    "scikit-learn": [
        "scikit-learn",
        "sklearn"
    ],

    "aws": [
        "aws",
        "amazon web services"
    ],

    "azure": [
        "azure",
        "microsoft azure"
    ],

    "gcp": [
        "gcp",
        "google cloud"
    ],

    "docker": [
        "docker"
    ],

    "kubernetes": [
        "kubernetes",
        "k8s"
    ],

    "pandas": [
        "pandas"
    ],

    "numpy": [
        "numpy"
    ],

    "spark": [
        "spark",
        "apache spark"
    ],

    "java": [
        "java"
    ],

    "javascript": [
        "javascript",
        "js"
    ],

    "react": [
        "react",
        "react.js"
    ],

    "django": [
        "django"
    ],

    "flask": [
        "flask"
    ],

    "fastapi": [
        "fastapi"
    ],

    "git": [
        "git",
        "github",
        "gitlab"
    ],

    "power bi": [
        "power bi",
        "powerbi"
    ],

    "tableau": [
        "tableau"
    ],

    "excel": [
        "excel",
        "microsoft excel"
    ],
}


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_required_experience(query):

    query_lower = query.lower()

    patterns = [

        r"(\d+(?:\.\d+)?)\+?\s*years?",

        r"(\d+(?:\.\d+)?)\+?\s*yrs?",
    ]

    values = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            query_lower
        )

        for match in matches:

            try:

                values.append(
                    float(match)
                )

            except ValueError:

                pass

    if values:

        return max(values)

    return 0


# ============================================================
# SKILL EXTRACTION FROM QUERY
# ============================================================

def extract_required_skills(query):

    query_lower = query.lower()

    required = []

    for canonical, aliases in SKILL_ALIASES.items():

        for alias in aliases:

            pattern = (
                r"(?<![a-z])"
                + re.escape(alias)
                + r"(?![a-z])"
            )

            if re.search(
                pattern,
                query_lower
            ):

                required.append(
                    canonical
                )

                break

    return required


# ============================================================
# SKILL MATCHING
# ============================================================

def calculate_skill_score(
    candidate_skills,
    required_skills
):

    candidate_lower = [
        skill.lower()
        for skill in candidate_skills
    ]

    matched = []

    for required in required_skills:

        aliases = SKILL_ALIASES.get(
            required,
            [required]
        )

        found = False

        for candidate in candidate_lower:

            for alias in aliases:

                if alias.lower() in candidate:

                    found = True

                    break

            if found:

                break

        if found:

            matched.append(
                required
            )

    if not required_skills:

        return 100, [], []

    score = (
        len(matched)
        / len(required_skills)
    ) * 100

    missing = [
        skill
        for skill in required_skills
        if skill not in matched
    ]

    return (
        score,
        matched,
        missing
    )


# ============================================================
# EXPERIENCE SCORE
# ============================================================

def calculate_experience_score(
    candidate_experience,
    required_experience
):

    if required_experience <= 0:

        return 100

    candidate_experience = float(
        candidate_experience or 0
    )

    score = (
        candidate_experience
        / required_experience
    ) * 100

    return min(
        score,
        100
    )


# ============================================================
# EDUCATION SCORE
# ============================================================

def calculate_education_score(
    education
):

    if education:

        return 100

    return 0


# ============================================================
# TF-IDF RELEVANCE
# ============================================================

def calculate_relevance(
    resumes,
    query
):

    documents = []

    for resume in resumes:

        text = resume.get(
            "raw_text",
            ""
        )

        documents.append(
            text
        )

    if not documents:

        return []

    documents_with_query = (
        documents + [query]
    )

    try:

        vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        matrix = vectorizer.fit_transform(
            documents_with_query
        )

        similarities = cosine_similarity(
            matrix[-1],
            matrix[:-1]
        )[0]

        return [
            float(value) * 100
            for value in similarities
        ]

    except ValueError:

        return [
            0
            for _ in resumes
        ]


# ============================================================
# MAIN SEARCH FUNCTION
# ============================================================

def search_resumes(
    resumes,
    query
):

    if not resumes:

        return []

    # --------------------------------------------------------
    # Extract requirements
    # --------------------------------------------------------

    required_skills = (
        extract_required_skills(
            query
        )
    )

    required_experience = (
        extract_required_experience(
            query
        )
    )

    # --------------------------------------------------------
    # Relevance scores
    # --------------------------------------------------------

    relevance_scores = (
        calculate_relevance(
            resumes,
            query
        )
    )

    results = []

    # --------------------------------------------------------
    # Score every candidate
    # --------------------------------------------------------

    for index, resume in enumerate(
        resumes
    ):

        candidate_skills = resume.get(
            "skills",
            []
        )

        candidate_experience = resume.get(
            "experience",
            0
        )

        education = resume.get(
            "education",
            []
        )

        # ----------------------------------------------------
        # Skills — 50%
        # ----------------------------------------------------

        skill_score, matched, missing = (
            calculate_skill_score(
                candidate_skills,
                required_skills
            )
        )

        # ----------------------------------------------------
        # Experience — 30%
        # ----------------------------------------------------

        experience_score = (
            calculate_experience_score(
                candidate_experience,
                required_experience
            )
        )

        # ----------------------------------------------------
        # Education — 10%
        # ----------------------------------------------------

        education_score = (
            calculate_education_score(
                education
            )
        )

        # ----------------------------------------------------
        # Relevance — 10%
        # ----------------------------------------------------

        relevance_score = (
            relevance_scores[index]
            if index < len(
                relevance_scores
            )
            else 0
        )

        # ----------------------------------------------------
        # FINAL SCORE
        # ----------------------------------------------------

        final_score = (

            skill_score * 0.50

            +

            experience_score * 0.30

            +

            education_score * 0.10

            +

            relevance_score * 0.10

        )

        # ----------------------------------------------------
        # Copy resume
        # ----------------------------------------------------

        candidate = resume.copy()

        candidate["score"] = round(
            final_score
        )

        candidate["matched_skills"] = (
            matched
        )

        candidate["missing_skills"] = (
            missing
        )

        candidate["score_breakdown"] = {

            "Skills": round(
                skill_score
            ),

            "Experience": round(
                experience_score
            ),

            "Education": round(
                education_score
            ),

            "Relevance": round(
                relevance_score
            ),
        }

        results.append(
            candidate
        )

    # --------------------------------------------------------
    # Rank candidates
    # --------------------------------------------------------

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results

