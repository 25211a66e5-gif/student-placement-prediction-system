CAREERPREDICT - CAREER ANALYSIS UPGRADE

Files:
1. assessment-result_career_analysis.html
   Replace:
   frontend/pages/assessment-result.html

2. career_analysis_api.py
   Copy to:
   backend/career_analysis_api.py

Then add these two lines to backend/app.py, after the existing
assessment_api import/call:

    from career_analysis_api import register_career_analysis_routes
    register_career_analysis_routes(app)

Do NOT replace your working app.py wholesale.

Restart:
    python app.py

The result page will show:
- Strengths
- Skill gaps
- Personalized recommendations
- Company eligibility

Company eligibility is calculated from the existing
company_requirements table. If no active company requirements have
been configured by an administrator, the page will explicitly say so
rather than inventing company criteria.
