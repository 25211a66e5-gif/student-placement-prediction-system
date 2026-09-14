from flask import request, jsonify
from database import get_connection
from ml.readiness_model import calculate_readiness_score
import random


# ============================================================
# ASSESSMENT CONFIGURATION
# ============================================================

ASSESSMENT_CONFIG = {
    "Technical": 15,
    "Aptitude": 10,
    "Logical Reasoning": 10,
    "Communication": 10,
    "Coding Concepts": 10
}


# ============================================================
# PUBLIC QUESTION
# ============================================================

def public_question(question):
    """
    Return only information that the student can see.

    The correct answer is NEVER sent to the frontend.
    """

    return {
        "id": question["id"],
        "section": question["section"],
        "topic": question["topic"],
        "question_text": question["question_text"],
        "options": {
            "A": question["option_a"],
            "B": question["option_b"],
            "C": question["option_c"],
            "D": question["option_d"]
        },
        "difficulty": question["difficulty"]
    }


# ============================================================
# RECENT QUESTIONS
# ============================================================

def get_recent_question_ids(cursor, user_id, limit=100):

    cursor.execute(
        """
        SELECT DISTINCT qa.question_id
        FROM question_attempts qa
        JOIN assessments a
            ON qa.assessment_id = a.id
        WHERE a.user_id = ?
        ORDER BY qa.id DESC
        LIMIT ?
        """,
        (user_id, limit)
    )

    rows = cursor.fetchall()

    return {
        row["question_id"]
        for row in rows
    }


# ============================================================
# SELECT RANDOM QUESTIONS
# ============================================================

def select_random_questions(
    cursor,
    section,
    branch,
    target_role,
    required_count,
    recent_ids
):

    # --------------------------------------------------------
    # Exact branch + exact role
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT *
        FROM questions
        WHERE section = ?
          AND is_active = 1
          AND branch = ?
          AND target_role = ?
        """,
        (
            section,
            branch,
            target_role
        )
    )

    exact_questions = cursor.fetchall()


    # --------------------------------------------------------
    # Same branch
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT *
        FROM questions
        WHERE section = ?
          AND is_active = 1
          AND branch = ?
        """,
        (
            section,
            branch
        )
    )

    branch_questions = cursor.fetchall()


    # --------------------------------------------------------
    # Same target role
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT *
        FROM questions
        WHERE section = ?
          AND is_active = 1
          AND target_role = ?
        """,
        (
            section,
            target_role
        )
    )

    role_questions = cursor.fetchall()


    # --------------------------------------------------------
    # General questions
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT *
        FROM questions
        WHERE section = ?
          AND is_active = 1
          AND branch IS NULL
          AND target_role IS NULL
        """,
        (section,)
    )

    general_questions = cursor.fetchall()


    # --------------------------------------------------------
    # Combine without duplicates
    # --------------------------------------------------------

    candidates = []
    seen_ids = set()

    for group in [
        exact_questions,
        branch_questions,
        role_questions,
        general_questions
    ]:

        for question in group:

            question_id = question["id"]

            if question_id not in seen_ids:

                candidates.append(question)

                seen_ids.add(question_id)


    # --------------------------------------------------------
    # Prefer questions not recently attempted
    # --------------------------------------------------------

    fresh_questions = [
        question
        for question in candidates
        if question["id"] not in recent_ids
    ]

    previously_used = [
        question
        for question in candidates
        if question["id"] in recent_ids
    ]


    random.shuffle(fresh_questions)
    random.shuffle(previously_used)


    selected = fresh_questions[:required_count]


    # --------------------------------------------------------
    # Use previously attempted questions only if necessary
    # --------------------------------------------------------

    remaining = (
        required_count
        - len(selected)
    )

    if remaining > 0:

        selected.extend(
            previously_used[:remaining]
        )


    # --------------------------------------------------------
    # Randomize final order
    # --------------------------------------------------------

    random.shuffle(selected)

    return selected[:required_count]


# ============================================================
# REGISTER ASSESSMENT ROUTES
# ============================================================

def register_assessment_routes(app):


    # ========================================================
    # START ASSESSMENT
    # ========================================================

    @app.post("/api/assessment/start")
    def start_assessment():

        data = request.get_json(
            silent=True
        ) or {}

        user_id = data.get("user_id")


        if not user_id:

            return jsonify({
                "error": "User ID is required."
            }), 400


        connection = get_connection()

        try:

            cursor = connection.cursor()


            # ------------------------------------------------
            # Get student profile
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT
                    branch,
                    target_job_role
                FROM student_profiles
                WHERE user_id = ?
                """,
                (user_id,)
            )

            profile = cursor.fetchone()


            if profile is None:

                return jsonify({
                    "error":
                        "Please complete your student profile first."
                }), 400


            branch = profile["branch"]

            target_role = profile[
                "target_job_role"
            ]


            # ------------------------------------------------
            # Resume unfinished assessment
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT id
                FROM assessments
                WHERE user_id = ?
                  AND status = 'in_progress'
                ORDER BY id DESC
                LIMIT 1
                """,
                (user_id,)
            )

            existing = cursor.fetchone()


            if existing:

                assessment_id = existing["id"]


                cursor.execute(
                    """
                    SELECT q.*
                    FROM question_attempts qa
                    JOIN questions q
                        ON qa.question_id = q.id
                    WHERE qa.assessment_id = ?
                    ORDER BY qa.id
                    """,
                    (assessment_id,)
                )

                existing_questions = (
                    cursor.fetchall()
                )


                if existing_questions:

                    return jsonify({

                        "message":
                            "Existing assessment resumed.",

                        "assessment_id":
                            assessment_id,

                        "branch":
                            branch,

                        "target_job_role":
                            target_role,

                        "total_questions":
                            len(existing_questions),

                        "questions": [
                            public_question(q)
                            for q in existing_questions
                        ]

                    }), 200


            # ------------------------------------------------
            # Recent questions
            # ------------------------------------------------

            recent_ids = (
                get_recent_question_ids(
                    cursor,
                    user_id
                )
            )


            # ------------------------------------------------
            # Select questions section by section
            # ------------------------------------------------

            selected_questions = []


            for section, count in (
                ASSESSMENT_CONFIG.items()
            ):

                section_questions = (
                    select_random_questions(
                        cursor,
                        section,
                        branch,
                        target_role,
                        count,
                        recent_ids
                    )
                )

                selected_questions.extend(
                    section_questions
                )


            # ------------------------------------------------
            # Make sure questions exist
            # ------------------------------------------------

            if not selected_questions:

                return jsonify({
                    "error":
                        "No assessment questions are available."
                }), 404


            # ------------------------------------------------
            # Randomize complete assessment
            # ------------------------------------------------

            random.shuffle(
                selected_questions
            )


            # ------------------------------------------------
            # Create assessment
            # ------------------------------------------------

            cursor.execute(
                """
                INSERT INTO assessments
                (
                    user_id,
                    branch,
                    target_job_role,
                    status,
                    total_questions
                )
                VALUES (?, ?, ?, 'in_progress', ?)
                """,
                (
                    user_id,
                    branch,
                    target_role,
                    len(selected_questions)
                )
            )

            assessment_id = cursor.lastrowid


            # ------------------------------------------------
            # Store selected questions
            # ------------------------------------------------

            for question in selected_questions:

                cursor.execute(
                    """
                    INSERT INTO question_attempts
                    (
                        assessment_id,
                        question_id,
                        selected_answer,
                        status,
                        is_correct
                    )
                    VALUES (
                        ?,
                        ?,
                        NULL,
                        'skipped',
                        0
                    )
                    """,
                    (
                        assessment_id,
                        question["id"]
                    )
                )


            connection.commit()


            # ------------------------------------------------
            # Return safe questions
            # ------------------------------------------------

            return jsonify({

                "message":
                    "Assessment created successfully.",

                "assessment_id":
                    assessment_id,

                "branch":
                    branch,

                "target_job_role":
                    target_role,

                "total_questions":
                    len(selected_questions),

                "questions": [
                    public_question(q)
                    for q in selected_questions
                ]

            }), 201


        except Exception as error:

            connection.rollback()

            return jsonify({

                "error":
                    "Unable to start assessment.",

                "message":
                    str(error)

            }), 500


        finally:

            connection.close()


    # ========================================================
    # SAVE ANSWER
    # ========================================================

    @app.post("/api/assessment/answer")
    def save_assessment_answer():

        data = request.get_json(
            silent=True
        ) or {}

        assessment_id = data.get(
            "assessment_id"
        )

        question_id = data.get(
            "question_id"
        )

        selected_answer = data.get(
            "selected_answer"
        )


        if not assessment_id:

            return jsonify({
                "error":
                    "Assessment ID is required."
            }), 400


        if not question_id:

            return jsonify({
                "error":
                    "Question ID is required."
            }), 400


        if selected_answer not in [
            "A",
            "B",
            "C",
            "D",
            None
        ]:

            return jsonify({
                "error":
                    "Invalid answer option."
            }), 400


        connection = get_connection()

        try:

            cursor = connection.cursor()


            # ------------------------------------------------
            # Verify assessment
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT status
                FROM assessments
                WHERE id = ?
                """,
                (assessment_id,)
            )

            assessment = cursor.fetchone()


            if assessment is None:

                return jsonify({
                    "error":
                        "Assessment not found."
                }), 404


            if assessment["status"] != "in_progress":

                return jsonify({
                    "error":
                        "Assessment is no longer active."
                }), 400


            # ------------------------------------------------
            # Verify question belongs to assessment
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT
                    qa.id,
                    q.correct_answer
                FROM question_attempts qa
                JOIN questions q
                    ON qa.question_id = q.id
                WHERE qa.assessment_id = ?
                  AND qa.question_id = ?
                """,
                (
                    assessment_id,
                    question_id
                )
            )

            question = cursor.fetchone()


            if question is None:

                return jsonify({
                    "error":
                        "Question does not belong to this assessment."
                }), 400


            # ------------------------------------------------
            # Determine status
            # ------------------------------------------------

            if selected_answer is None:

                status = "skipped"

                is_correct = 0

            elif (
                selected_answer
                == question["correct_answer"]
            ):

                status = "correct"

                is_correct = 1

            else:

                status = "wrong"

                is_correct = 0


            # ------------------------------------------------
            # Save answer
            # ------------------------------------------------

            cursor.execute(
                """
                UPDATE question_attempts
                SET
                    selected_answer = ?,
                    status = ?,
                    is_correct = ?,
                    answered_at = CURRENT_TIMESTAMP
                WHERE assessment_id = ?
                  AND question_id = ?
                """,
                (
                    selected_answer,
                    status,
                    is_correct,
                    assessment_id,
                    question_id
                )
            )


            connection.commit()


            return jsonify({

                "message":
                    "Answer saved.",

                "status":
                    status

            }), 200


        except Exception as error:

            connection.rollback()

            return jsonify({

                "error":
                    "Unable to save answer.",

                "message":
                    str(error)

            }), 500


        finally:

            connection.close()


    # ========================================================
    # SUBMIT ASSESSMENT
    # ========================================================

    @app.post("/api/assessment/submit")
    def submit_assessment():

        data = request.get_json(
            silent=True
        ) or {}

        assessment_id = data.get(
            "assessment_id"
        )


        if not assessment_id:

            return jsonify({
                "error":
                    "Assessment ID is required."
            }), 400


        connection = get_connection()

        try:

            cursor = connection.cursor()


            # ------------------------------------------------
            # Get assessment
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT *
                FROM assessments
                WHERE id = ?
                """,
                (assessment_id,)
            )

            assessment = cursor.fetchone()


            if assessment is None:

                return jsonify({
                    "error":
                        "Assessment not found."
                }), 404


            if assessment["status"] == "completed":

                return jsonify({
                    "error":
                        "Assessment has already been submitted."
                }), 400


            # ------------------------------------------------
            # Get attempts
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT
                    qa.*,
                    q.section,
                    q.topic
                FROM question_attempts qa
                JOIN questions q
                    ON qa.question_id = q.id
                WHERE qa.assessment_id = ?
                """,
                (assessment_id,)
            )

            attempts = cursor.fetchall()


            total = len(attempts)


            answered = sum(
                1
                for attempt in attempts
                if attempt["selected_answer"]
                is not None
            )


            skipped = (
                total - answered
            )


            correct = sum(
                1
                for attempt in attempts
                if attempt["is_correct"] == 1
            )


            wrong = (
                answered - correct
            )


            score = (
                round(
                    correct / total * 100,
                    2
                )
                if total > 0
                else 0
            )

            
        

            # ------------------------------------------------
            # Section scores
            # ------------------------------------------------

            section_scores = {}


            for section in (
                ASSESSMENT_CONFIG
            ):

                section_attempts = [
                    attempt
                    for attempt in attempts
                    if attempt["section"]
                    == section
                ]


                section_total = (
                    len(section_attempts)
                )


                section_correct = sum(
                    1
                    for attempt
                    in section_attempts
                    if attempt["is_correct"]
                    == 1
                )


                section_scores[section] = (

                    round(
                        section_correct
                        / section_total
                        * 100,
                        2
                    )

                    if section_total > 0

                    else 0

                )
# ------------------------------------------------
            # Calculate Job Readiness Score
            # ------------------------------------------------

            readiness_score = calculate_readiness_score(
                technical_score=section_scores.get(
                    "Technical", 0
                ),
                aptitude_score=section_scores.get(
                    "Aptitude", 0
                ),
                logical_score=section_scores.get(
                    "Logical Reasoning", 0
                ),
                communication_score=section_scores.get(
                    "Communication", 0
                ),
                coding_concepts_score=section_scores.get(
                    "Coding Concepts", 0
                ),
                coding_test_score=0
            )                 

            # ------------------------------------------------
            # Mark completed
            # ------------------------------------------------

            cursor.execute(
                """
                UPDATE assessments
                SET
                    completed_at =
                        CURRENT_TIMESTAMP,

                    status =
                        'completed',

                    total_questions = ?,

                    answered_questions = ?,

                    skipped_questions = ?,

                    correct_answers = ?,

                    wrong_answers = ?,

                    score = ?

                WHERE id = ?
                """,
                (
                    total,
                    answered,
                    skipped,
                    correct,
                    wrong,
                    score,
                    assessment_id
                )
            )


            # ------------------------------------------------
            # Create result
            # ------------------------------------------------

            user_id = assessment["user_id"]


            cursor.execute(
                """
                INSERT OR REPLACE INTO assessment_results
                (
                    assessment_id,
                    user_id,
                    technical_score,
                    aptitude_score,
                    logical_score,
                    communication_score,
                    coding_concepts_score,
                    coding_test_score,
                    overall_score,
                    readiness_score,
                    placement_probability
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, 0)
                """,
                (
                    assessment_id,
                    user_id,

                    section_scores.get(
                        "Technical",
                        0
                    ),

                    section_scores.get(
                        "Aptitude",
                        0
                    ),

                    section_scores.get(
                        "Logical Reasoning",
                        0
                    ),

                    section_scores.get(
                        "Communication",
                        0
                    ),

                    section_scores.get(
                        "Coding Concepts",
                        0
                    ),

                    score,

                    readiness_score
                )
            )


            connection.commit()


            return jsonify({

                "message":
                    "Assessment submitted successfully.",

                "assessment_id":
                    assessment_id,

                "total_questions":
                    total,

                "answered_questions":
                    answered,

                "skipped_questions":
                    skipped,

                "correct_answers":
                    correct,

                "wrong_answers":
                    wrong,

                "score":
                    score,

                "section_scores":
                    section_scores

            }), 200


        except Exception as error:

            connection.rollback()

            return jsonify({

                "error":
                    "Unable to submit assessment.",

                "message":
                    str(error)

            }), 500


        finally:

            connection.close()


    # ========================================================
    # GET RESULT
    # ========================================================

    @app.get(
        "/api/assessment/<int:assessment_id>/result"
    )
    def get_assessment_result(
        assessment_id
    ):

        connection = get_connection()

        try:

            cursor = connection.cursor()


            cursor.execute(
                """
                SELECT
                    a.*,

                    ar.technical_score,
                    ar.aptitude_score,
                    ar.logical_score,
                    ar.communication_score,
                    ar.coding_concepts_score,
                    ar.coding_test_score,
                    ar.overall_score,
                    ar.readiness_score,
                    ar.placement_probability

                FROM assessments a

                LEFT JOIN assessment_results ar
                    ON a.id = ar.assessment_id

                WHERE a.id = ?
                """,
                (assessment_id,)
            )


            result = cursor.fetchone()


            if result is None:

                return jsonify({
                    "error":
                        "Assessment result not found."
                }), 404


            # ------------------------------------------------
            # Question review
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT
                    qa.question_id,
                    qa.selected_answer,
                    qa.status,
                    qa.is_correct,

                    q.section,
                    q.topic,
                    q.question_text,

                    q.option_a,
                    q.option_b,
                    q.option_c,
                    q.option_d,

                    q.correct_answer,
                    q.explanation

                FROM question_attempts qa

                JOIN questions q
                    ON qa.question_id = q.id

                WHERE qa.assessment_id = ?

                ORDER BY qa.id
                """,
                (assessment_id,)
            )


            attempts = cursor.fetchall()


            review = []


            for attempt in attempts:

                review.append({

                    "question_id":
                        attempt["question_id"],

                    "section":
                        attempt["section"],

                    "topic":
                        attempt["topic"],

                    "question_text":
                        attempt["question_text"],

                    "options": {

                        "A":
                            attempt["option_a"],

                        "B":
                            attempt["option_b"],

                        "C":
                            attempt["option_c"],

                        "D":
                            attempt["option_d"]

                    },

                    "selected_answer":
                        attempt["selected_answer"],

                    "correct_answer":
                        attempt["correct_answer"],

                    "status":
                        attempt["status"],

                    "explanation":
                        attempt["explanation"]

                })


            return jsonify({

                "assessment": {

                    "id":
                        result["id"],

                    "status":
                        result["status"],

                    "score":
                        result["score"],

                    "total_questions":
                        result["total_questions"],

                    "answered_questions":
                        result["answered_questions"],

                    "skipped_questions":
                        result["skipped_questions"],

                    "correct_answers":
                        result["correct_answers"],

                    "wrong_answers":
                        result["wrong_answers"]

                },

                "section_scores": {

                    "Technical":
                        result["technical_score"],

                    "Aptitude":
                        result["aptitude_score"],

                    "Logical Reasoning":
                        result["logical_score"],

                    "Communication":
                        result["communication_score"],

                    "Coding Concepts":
                        result["coding_concepts_score"],

                    "Coding Test":
                        result["coding_test_score"]

                },

                "readiness_score":
                    result["readiness_score"],

                "placement_probability":
                    result["placement_probability"],

                "review":
                    review

            }), 200


        except Exception as error:

            return jsonify({

                "error":
                    "Unable to retrieve assessment result.",

                "message":
                    str(error)

            }), 500


        finally:

            connection.close()


    # ========================================================
    # SAVE CODING TEST SCORE
    # ========================================================

    @app.post("/api/coding-test/save")
    def save_coding_test_score():

        data = request.get_json(silent=True) or {}

        assessment_id = data.get("assessment_id")
        score = data.get("score")

        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        if not assessment_id:
            return jsonify({
                "error": "Assessment ID is required."
            }), 400

        if score is None:
            return jsonify({
                "error": "Coding test score is required."
            }), 400

        try:
            score = float(score)
        except (TypeError, ValueError):
            return jsonify({
                "error": "Coding test score must be a number."
            }), 400

        if score < 0 or score > 100:
            return jsonify({
                "error": "Coding test score must be between 0 and 100."
            }), 400

        connection = get_connection()

        try:

            cursor = connection.cursor()

            # ------------------------------------------------
            # Verify completed assessment
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT
                    id,
                    user_id,
                    status
                FROM assessments
                WHERE id = ?
                """,
                (assessment_id,)
            )

            assessment = cursor.fetchone()

            if assessment is None:
                return jsonify({
                    "error": "Assessment not found."
                }), 404

            if assessment["status"] != "completed":
                return jsonify({
                    "error":
                        "Coding test can only be saved "
                        "after completing the assessment."
                }), 400

            # ------------------------------------------------
            # Get existing assessment result
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT
                    technical_score,
                    aptitude_score,
                    logical_score,
                    communication_score,
                    coding_concepts_score
                FROM assessment_results
                WHERE assessment_id = ?
                """,
                (assessment_id,)
            )

            result = cursor.fetchone()

            if result is None:
                return jsonify({
                    "error": "Assessment result not found."
                }), 404

            # ------------------------------------------------
            # Recalculate Job Readiness
            # ------------------------------------------------

            readiness_score = calculate_readiness_score(
                technical_score=result["technical_score"] or 0,
                aptitude_score=result["aptitude_score"] or 0,
                logical_score=result["logical_score"] or 0,
                communication_score=result["communication_score"] or 0,
                coding_concepts_score=result["coding_concepts_score"] or 0,
                coding_test_score=score
            )

            # ------------------------------------------------
            # Calculate Overall Assessment Score
            #
            # Overall score represents the average performance
            # across all six assessment components:
            #   1. Technical
            #   2. Aptitude
            #   3. Logical Reasoning
            #   4. Communication
            #   5. Coding Concepts
            #   6. Coding Test
            #
            # Job Readiness is kept separate and uses the
            # weighted readiness model.
            # ------------------------------------------------

            component_scores = [
                result["technical_score"] or 0,
                result["aptitude_score"] or 0,
                result["logical_score"] or 0,
                result["communication_score"] or 0,
                result["coding_concepts_score"] or 0,
                score
            ]

            overall_score = round(
                sum(component_scores)
                / len(component_scores),
                2
            )

            # ------------------------------------------------
            # Save coding score + overall score + readiness score
            # ------------------------------------------------

            cursor.execute(
                """
                UPDATE assessment_results
                SET
                    coding_test_score = ?,
                    overall_score = ?,
                    readiness_score = ?
                WHERE assessment_id = ?
                """,
                (
                    round(score, 2),
                    overall_score,
                    round(readiness_score, 2),
                    assessment_id
                )
            )

            # Keep the main assessment record synchronized.
            cursor.execute(
                """
                UPDATE assessments
                SET
                    score = ?
                WHERE id = ?
                """,
                (
                    overall_score,
                    assessment_id
                )
            )

            connection.commit()

            return jsonify({
                "message":
                    "Coding test score saved successfully.",
                "assessment_id":
                    assessment_id,
                "coding_test_score":
                    round(score, 2),
                "overall_score":
                    overall_score,
                "readiness_score":
                    round(readiness_score, 2)
            }), 200

        except Exception as error:

            connection.rollback()

            return jsonify({
                "error":
                    "Unable to save coding test score.",
                "message":
                    str(error)
            }), 500

        finally:

            connection.close()

