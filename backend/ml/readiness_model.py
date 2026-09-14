# ============================================================
# JOB READINESS MODEL
# Student Placement Prediction System using Machine Learning
# ============================================================


READINESS_WEIGHTS = {
    "Technical": 0.30,
    "Aptitude": 0.15,
    "Logical Reasoning": 0.15,
    "Communication": 0.15,
    "Coding Concepts": 0.15,
    "Coding Test": 0.10
}


def calculate_readiness_score(
    technical_score=0,
    aptitude_score=0,
    logical_score=0,
    communication_score=0,
    coding_concepts_score=0,
    coding_test_score=0
):
    """
    Calculate the student's Job Readiness Score.

    All section scores are expected to be percentages
    between 0 and 100.

    Returns:
        float: Job Readiness Score between 0 and 100.
    """

    scores = {
        "Technical": technical_score,
        "Aptitude": aptitude_score,
        "Logical Reasoning": logical_score,
        "Communication": communication_score,
        "Coding Concepts": coding_concepts_score,
        "Coding Test": coding_test_score
    }

    total_score = 0

    for section, weight in READINESS_WEIGHTS.items():

        try:
            score = float(scores.get(section, 0))
        except (TypeError, ValueError):
            score = 0

        # Keep every score within the valid range.
        score = max(0, min(100, score))

        total_score += score * weight

    return round(total_score, 2)


def get_readiness_level(score):
    """
    Convert the numerical readiness score
    into an easy-to-understand readiness level.
    """

    score = float(score)

    if score >= 85:
        return "Excellent"

    if score >= 70:
        return "Good"

    if score >= 50:
        return "Moderate"

    return "Needs Improvement"


def get_readiness_message(score):
    """
    Generate a short interpretation of the
    student's Job Readiness Score.
    """

    level = get_readiness_level(score)

    messages = {
        "Excellent":
            "The student demonstrates strong preparation "
            "for the selected job role.",

        "Good":
            "The student demonstrates good preparation "
            "with some areas that can still be improved.",

        "Moderate":
            "The student has a developing skill foundation "
            "and should strengthen weaker areas before placement.",

        "Needs Improvement":
            "The student should focus on strengthening "
            "fundamental technical and employability skills."
    }

    return messages[level]