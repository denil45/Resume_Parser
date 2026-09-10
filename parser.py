import re
import fitz


# ============================================================
# SKILLS DATABASE
# ============================================================

SKILLS_DATABASE = [

    # Programming
    "python",
    "java",
    "c++",
    "c#",
    "javascript",
    "typescript",
    "r",
    "scala",
    "go",

    # Data
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "oracle",

    # Data Science
    "pandas",
    "numpy",
    "scikit-learn",
    "matplotlib",
    "seaborn",

    # Machine Learning
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "natural language processing",
    "nlp",
    "computer vision",

    # ML Frameworks
    "tensorflow",
    "pytorch",
    "keras",
    "xgboost",
    "lightgbm",

    # Cloud
    "aws",
    "azure",
    "gcp",
    "google cloud",

    # DevOps
    "docker",
    "kubernetes",
    "jenkins",
    "git",
    "github",
    "gitlab",

    # Big Data
    "spark",
    "hadoop",
    "kafka",

    # Web
    "react",
    "angular",
    "node.js",
    "django",
    "flask",
    "fastapi",

    # Other
    "excel",
    "power bi",
    "tableau",
    "data analysis",
    "statistics",
]


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(file):

    """
    Extract text from an uploaded PDF using PyMuPDF.
    """

    file_bytes = file.read()

    document = fitz.open(
        stream=file_bytes,
        filetype="pdf"
    )

    text = ""

    for page in document:

        text += page.get_text()

        text += "\n"

    document.close()

    return text


# ============================================================
# EMAIL EXTRACTION
# ============================================================

def extract_email(text):

    pattern = (
        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    )

    match = re.search(
        pattern,
        text
    )

    if match:

        return match.group(0)

    return "Not found"


# ============================================================
# PHONE EXTRACTION
# ============================================================

def extract_phone(text):

    patterns = [

        r"\+91[\s-]?\d{5}[\s-]?\d{5}",

        r"\+91[\s-]?\d{10}",

        r"\b\d{10}\b",

        r"\+\d{1,3}[\s-]?\d{7,12}",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            return match.group(0)

    return "Not found"


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # Try first few lines
    for line in lines[:10]:

        lower = line.lower()

        # Ignore obvious headings
        ignored = [
            "resume",
            "curriculum vitae",
            "cv",
            "profile",
            "contact",
            "objective",
        ]

        if any(
            word in lower
            for word in ignored
        ):
            continue

        # Ignore lines containing email
        if "@" in line:
            continue

        # Ignore lines containing phone
        if re.search(
            r"\d{7,}",
            line
        ):
            continue

        # Name usually has 2-4 words
        words = line.split()

        if 2 <= len(words) <= 4:

            if all(
                re.match(
                    r"^[A-Za-z.'-]+$",
                    word
                )
                for word in words
            ):

                return line

    return "Unknown Candidate"


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_skills(text):

    text_lower = text.lower()

    found = []

    for skill in SKILLS_DATABASE:

        # Flexible matching
        pattern = (
            r"(?<![a-z])"
            + re.escape(skill)
            + r"(?![a-z])"
        )

        if re.search(
            pattern,
            text_lower
        ):

            found.append(skill)

    return sorted(
        found
    )


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_experience(text):

    text_lower = text.lower()

    patterns = [

        r"(\d+(?:\.\d+)?)\+?\s*years?\s+of\s+experience",

        r"(\d+(?:\.\d+)?)\+?\s*years?\s+experience",

        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\+?\s*years?",

        r"(\d+(?:\.\d+)?)\+?\s*yrs?\s+experience",
    ]

    values = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text_lower
        )

        for match in matches:

            try:

                values.append(
                    float(match)
                )

            except ValueError:

                pass

    if values:

        # Maximum is usually safer
        return max(values)

    # --------------------------------------------------------
    # Try date ranges
    # --------------------------------------------------------

    years = []

    date_pattern = (
        r"(20\d{2})"
        r"\s*[-–to]+\s*"
        r"(20\d{2}|present|current)"
    )

    matches = re.findall(
        date_pattern,
        text_lower
    )

    current_year = 2026

    for start, end in matches:

        try:

            start_year = int(start)

            if end in [
                "present",
                "current"
            ]:

                end_year = current_year

            else:

                end_year = int(end)

            if end_year >= start_year:

                years.append(
                    end_year - start_year
                )

        except ValueError:

            pass

    if years:

        return max(years)

    return 0


# ============================================================
# EDUCATION EXTRACTION
# ============================================================

def extract_education(text):

    education_keywords = [

        "b.tech",
        "btech",
        "b.e",
        "be ",
        "bachelor",
        "b.sc",
        "bsc",
        "bca",
        "m.tech",
        "mtech",
        "m.e",
        "me ",
        "master",
        "m.sc",
        "msc",
        "mca",
        "mba",
        "phd",
        "ph.d",
        "doctorate",
        "degree",
    ]

    results = []

    for line in text.splitlines():

        line = line.strip()

        if not line:

            continue

        lower = line.lower()

        if any(
            keyword in lower
            for keyword in education_keywords
        ):

            if line not in results:

                results.append(line)

    return results[:10]


# ============================================================
# MAIN PARSER
# ============================================================

def parse_resume(file):

    """
    Convert a PDF resume into a structured dictionary.
    """

    text = extract_text_from_pdf(
        file
    )

    if not text.strip():

        raise ValueError(
            "No readable text found in PDF."
        )

    resume = {

        "name": extract_name(
            text
        ),

        "email": extract_email(
            text
        ),

        "phone": extract_phone(
            text
        ),

        "skills": extract_skills(
            text
        ),

        "experience": extract_experience(
            text
        ),

        "education": extract_education(
            text
        ),

        "raw_text": text,
    }

    return resume
