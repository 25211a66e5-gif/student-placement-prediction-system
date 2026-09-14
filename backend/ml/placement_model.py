from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "placement_model.joblib"

_model = joblib.load(MODEL_PATH)


def predict_placement_probability(
    cgpa,
    branch,
    internships_count,
    projects_count,
    certifications_count,
    aptitude_score,
    communication_skill_score,
    logical_reasoning_skill_score,
    backlogs,
):
    data = pd.DataFrame([{
        "cgpa": float(cgpa),
        "branch": branch,
        "internships_count": int(internships_count),
        "projects_count": int(projects_count),
        "certifications_count": int(certifications_count),
        "aptitude_score": float(aptitude_score),
        "communication_skill_score": float(communication_skill_score),
        "logical_reasoning_score": float(logical_reasoning_skill_score),
        "backlogs": int(backlogs),
    }])

    probability = float(_model.predict_proba(data)[0][1]) * 100
    prediction = (
        "Likely to be Placed"
        if probability >= 50
        else "Placement Risk"
    )
    return round(probability, 2), prediction
