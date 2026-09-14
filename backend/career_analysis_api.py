from flask import jsonify
from database import get_connection
import json


def ensure_company_requirements_columns():
    connection = get_connection()
    try:
        connection.execute("""CREATE TABLE IF NOT EXISTS company_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL UNIQUE,
            minimum_tenth_percentage REAL NOT NULL DEFAULT 0,
            minimum_twelfth_percentage REAL NOT NULL DEFAULT 0,
            minimum_cgpa REAL NOT NULL DEFAULT 0,
            maximum_backlogs INTEGER NOT NULL DEFAULT 999,
            eligible_branches TEXT,
            minimum_graduation_year INTEGER,
            maximum_graduation_year INTEGER,
            minimum_assessment_score REAL NOT NULL DEFAULT 0,
            minimum_coding_test_score REAL NOT NULL DEFAULT 0,
            minimum_interview_score REAL NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        cols = {r[1] for r in connection.execute("PRAGMA table_info(company_requirements)").fetchall()}
        for name in ("minimum_assessment_score", "minimum_coding_test_score", "minimum_interview_score"):
            if name not in cols:
                connection.execute(f"ALTER TABLE company_requirements ADD COLUMN {name} REAL NOT NULL DEFAULT 0")
        connection.commit()
    finally:
        connection.close()


def parse_branches(value):
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(x).strip().lower() for x in parsed if str(x).strip()]
    except Exception:
        pass
    return [x.strip().lower() for x in str(value).split(",") if x.strip()]


def check_year(year, minimum, maximum):
    if year is None:
        return False if minimum is not None or maximum is not None else True
    if minimum is not None and year < minimum:
        return False
    if maximum is not None and year > maximum:
        return False
    return True


def register_career_analysis_routes(app):
    ensure_company_requirements_columns()

    @app.get("/api/career-analysis/<int:assessment_id>")
    def career_analysis(assessment_id):
        connection = get_connection()
        try:
            result = connection.execute("""
                SELECT ar.*, a.user_id, a.branch, a.target_job_role,
                       sp.tenth_percentage, sp.twelfth_percentage, sp.cgpa,
                       sp.graduation_year, sp.backlogs
                FROM assessment_results ar
                JOIN assessments a ON a.id = ar.assessment_id
                LEFT JOIN student_profiles sp ON sp.user_id = a.user_id
                WHERE ar.assessment_id = ?
            """, (assessment_id,)).fetchone()
            if result is None:
                return jsonify({"error": "Assessment result not found."}), 404

            # Use the latest technical interview score for this assessment when available.
            interview = connection.execute("""
                SELECT score, status, answered_questions, skipped_questions
                FROM technical_interviews
                WHERE assessment_id = ?
                ORDER BY id DESC LIMIT 1
            """, (assessment_id,)).fetchone()
            interview_score = float(interview["score"] or 0) if interview else 0.0

            section_scores = {
                "Technical": float(result["technical_score"] or 0),
                "Aptitude": float(result["aptitude_score"] or 0),
                "Logical Reasoning": float(result["logical_score"] or 0),
                "Communication": float(result["communication_score"] or 0),
                "Coding Concepts": float(result["coding_concepts_score"] or 0),
                "Coding Test": float(result["coding_test_score"] or 0),
                "Technical Interview": interview_score,
            }

            strengths = [name for name, score in sorted(section_scores.items(), key=lambda x: x[1], reverse=True) if score >= 70][:3]
            weaknesses = [name for name, score in sorted(section_scores.items(), key=lambda x: x[1]) if score < 70][:3]
            readiness = float(result["readiness_score"] or 0)
            recommendations = []
            for item in weaknesses:
                recommendations.append(f"Improve {item} through focused practice and repeated mock tests.")
            if int(result["backlogs"] or 0) > 0:
                recommendations.append("Work toward clearing active backlogs because many recruiters apply backlog limits.")
            if readiness < 70:
                recommendations.append("Complete another assessment, coding test and simulated interview after targeted preparation.")

            companies = connection.execute("SELECT * FROM company_requirements WHERE is_active = 1 ORDER BY company_name COLLATE NOCASE").fetchall()
            company_eligibility = []
            for company in companies:
                reasons = []
                checks = []
                tenth = float(result["tenth_percentage"] or 0)
                twelfth = float(result["twelfth_percentage"] or 0)
                cgpa = float(result["cgpa"] or 0)
                backlogs = int(result["backlogs"] or 0)
                branch = str(result["branch"] or "").strip()
                grad_year = result["graduation_year"]
                assessment_score = float(result["overall_score"] or 0)
                coding_score = float(result["coding_test_score"] or 0)

                def add(label, passed, reason):
                    checks.append({"criterion": label, "passed": bool(passed)})
                    if not passed:
                        reasons.append(reason)

                add("10th percentage", tenth >= float(company["minimum_tenth_percentage"] or 0), f'10th percentage {tenth:.1f}% is below the required {float(company["minimum_tenth_percentage"] or 0):.1f}%.')
                add("12th percentage", twelfth >= float(company["minimum_twelfth_percentage"] or 0), f'12th percentage {twelfth:.1f}% is below the required {float(company["minimum_twelfth_percentage"] or 0):.1f}%.')
                add("CGPA", cgpa >= float(company["minimum_cgpa"] or 0), f'CGPA {cgpa:.2f} is below the required {float(company["minimum_cgpa"] or 0):.2f}.')
                add("Backlogs", backlogs <= int(company["maximum_backlogs"] if company["maximum_backlogs"] is not None else 999), f'Backlogs ({backlogs}) exceed the allowed maximum of {int(company["maximum_backlogs"] or 0)}.')

                branches = parse_branches(company["eligible_branches"])
                branch_passed = not branches or branch.lower() in branches
                add("Branch", branch_passed, f'Branch {branch or "Not provided"} is not in the eligible branch list.')
                year_passed = check_year(grad_year, company["minimum_graduation_year"], company["maximum_graduation_year"])
                add("Graduation year", year_passed, "Graduation year does not match the configured company range.")

                min_assessment = float(company["minimum_assessment_score"] or 0)
                add("Assessment score", assessment_score >= min_assessment, f'Assessment score {assessment_score:.1f}% is below the required {min_assessment:.1f}%.')
                min_coding = float(company["minimum_coding_test_score"] or 0)
                add("Coding Test", coding_score >= min_coding, f'Coding Test score {coding_score:.1f}% is below the required {min_coding:.1f}%.')
                min_interview = float(company["minimum_interview_score"] or 0)
                interview_completed = interview is not None and str(interview["status"] or "").lower() == "completed"
                interview_passed = interview_completed and interview_score >= min_interview
                if not interview_completed:
                    reasons.append("AI-Simulated Technical Interview has not been completed yet.")
                    checks.append({"criterion": "Technical Interview", "passed": False, "score": interview_score, "required": min_interview})
                else:
                    add("Technical Interview", interview_score >= min_interview, f'Technical Interview score {interview_score:.1f}% is below the required {min_interview:.1f}%.')

                company_eligibility.append({
                    "company_name": company["company_name"],
                    "eligible": len(reasons) == 0,
                    "reasons": reasons,
                    "checks": checks,
                    "criteria": {
                        "minimum_assessment_score": min_assessment,
                        "minimum_coding_test_score": min_coding,
                        "minimum_interview_score": min_interview,
                    }
                })

            return jsonify({
                "strengths": strengths,
                "weaknesses": weaknesses,
                "recommendations": recommendations[:5],
                "company_eligibility": company_eligibility,
                "performance": {
                    "assessment_score": float(result["overall_score"] or 0),
                    "coding_test_score": float(result["coding_test_score"] or 0),
                    "technical_interview_score": interview_score,
                    "readiness_score": readiness,
                }
            }), 200
        finally:
            connection.close()
