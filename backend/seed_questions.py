from database import get_connection


# ============================================================
# CAREERPREDICT QUESTION BANK
# ============================================================

QUESTIONS = [

    # ========================================================
    # TECHNICAL - COMPUTER SCIENCE
    # ========================================================

    {
        "section": "Technical",
        "topic": "DBMS",
        "question_text": "Which normal form removes partial dependency?",
        "option_a": "1NF",
        "option_b": "2NF",
        "option_c": "3NF",
        "option_d": "BCNF",
        "correct_answer": "B",
        "explanation": "Second Normal Form removes partial dependency of non-key attributes on part of a composite key.",
        "difficulty": "Easy",
        "branch": "Computer Science",
        "target_role": "Software Developer"
    },

    {
        "section": "Technical",
        "topic": "DBMS",
        "question_text": "Which SQL command is used to remove a table completely?",
        "option_a": "DELETE",
        "option_b": "REMOVE",
        "option_c": "DROP",
        "option_d": "CLEAR",
        "correct_answer": "C",
        "explanation": "DROP TABLE removes the table structure and its data.",
        "difficulty": "Easy",
        "branch": "Computer Science",
        "target_role": "Software Developer"
    },

    {
        "section": "Technical",
        "topic": "Operating Systems",
        "question_text": "Which of the following is responsible for managing processes?",
        "option_a": "Compiler",
        "option_b": "Operating System",
        "option_c": "Database",
        "option_d": "Browser",
        "correct_answer": "B",
        "explanation": "The operating system manages processes, memory, files and hardware resources.",
        "difficulty": "Easy",
        "branch": "Computer Science",
        "target_role": "Software Developer"
    },

    {
        "section": "Technical",
        "topic": "Operating Systems",
        "question_text": "Which scheduling algorithm uses a time quantum?",
        "option_a": "FCFS",
        "option_b": "SJF",
        "option_c": "Round Robin",
        "option_d": "Priority Scheduling",
        "correct_answer": "C",
        "explanation": "Round Robin scheduling assigns each process a fixed time quantum.",
        "difficulty": "Easy",
        "branch": "Computer Science",
        "target_role": "Software Developer"
    },

    {
        "section": "Technical",
        "topic": "Computer Networks",
        "question_text": "Which protocol is commonly used to transfer web pages?",
        "option_a": "HTTP",
        "option_b": "FTP",
        "option_c": "SMTP",
        "option_d": "SSH",
        "correct_answer": "A",
        "explanation": "HTTP is the standard application-layer protocol used for transferring web resources.",
        "difficulty": "Easy",
        "branch": "Computer Science",
        "target_role": "Software Developer"
    },

    {
        "section": "Technical",
        "topic": "Computer Networks",
        "question_text": "Which device forwards packets between different networks?",
        "option_a": "Switch",
        "option_b": "Hub",
        "option_c": "Router",
        "option_d": "Repeater",
        "correct_answer": "C",
        "explanation": "A router forwards packets between different networks using IP addresses.",
        "difficulty": "Easy",
        "branch": "Computer Science",
        "target_role": "Software Developer"
    },

    {
        "section": "Technical",
        "topic": "Data Structures",
        "question_text": "Which data structure follows LIFO?",
        "option_a": "Queue",
        "option_b": "Stack",
        "option_c": "Linked List",
        "option_d": "Tree",
        "correct_answer": "B",
        "explanation": "A stack follows Last In, First Out.",
        "difficulty": "Easy",
        "branch": "Computer Science",
        "target_role": "Software Developer"
    },

    {
        "section": "Technical",
        "topic": "Data Structures",
        "question_text": "Which data structure is commonly used for BFS?",
        "option_a": "Stack",
        "option_b": "Queue",
        "option_c": "Heap",
        "option_d": "Tree",
        "correct_answer": "B",
        "explanation": "Breadth First Search uses a queue to process vertices level by level.",
        "difficulty": "Medium",
        "branch": "Computer Science",
        "target_role": "Software Developer"
    },

    {
        "section": "Technical",
        "topic": "Algorithms",
        "question_text": "What is the average time complexity of binary search?",
        "option_a": "O(n)",
        "option_b": "O(n²)",
        "option_c": "O(log n)",
        "option_d": "O(1)",
        "correct_answer": "C",
        "explanation": "Binary search halves the search space at every step, giving O(log n) average complexity.",
        "difficulty": "Medium",
        "branch": "Computer Science",
        "target_role": "Software Developer"
    },

    {
        "section": "Technical",
        "topic": "OOP",
        "question_text": "Which OOP concept allows the same interface to have different implementations?",
        "option_a": "Encapsulation",
        "option_b": "Inheritance",
        "option_c": "Polymorphism",
        "option_d": "Abstraction",
        "correct_answer": "C",
        "explanation": "Polymorphism allows the same interface or method call to behave differently depending on the object.",
        "difficulty": "Easy",
        "branch": "Computer Science",
        "target_role": "Software Developer"
    },

    {
        "section": "Technical",
        "topic": "Java",
        "question_text": "Which keyword is used to inherit a class in Java?",
        "option_a": "implements",
        "option_b": "inherits",
        "option_c": "extends",
        "option_d": "super",
        "correct_answer": "C",
        "explanation": "The extends keyword is used when one Java class inherits another class.",
        "difficulty": "Easy",
        "branch": "Computer Science",
        "target_role": "Java Developer"
    },

    {
        "section": "Technical",
        "topic": "Java",
        "question_text": "Which method is the entry point of a Java application?",
        "option_a": "start()",
        "option_b": "main()",
        "option_c": "run()",
        "option_d": "execute()",
        "correct_answer": "B",
        "explanation": "Java applications normally begin execution from public static void main(String[] args).",
        "difficulty": "Easy",
        "branch": "Computer Science",
        "target_role": "Java Developer"
    },

    {
        "section": "Technical",
        "topic": "Python",
        "question_text": "Which symbol is used to create a Python list?",
        "option_a": "()",
        "option_b": "{}",
        "option_c": "[]",
        "option_d": "<>",
        "correct_answer": "C",
        "explanation": "Square brackets are used to create Python lists.",
        "difficulty": "Easy",
        "branch": "Computer Science",
        "target_role": "Python Developer"
    },

    {
        "section": "Technical",
        "topic": "Python",
        "question_text": "Which keyword defines a function in Python?",
        "option_a": "function",
        "option_b": "def",
        "option_c": "func",
        "option_d": "define",
        "correct_answer": "B",
        "explanation": "Python uses the def keyword to define a function.",
        "difficulty": "Easy",
        "branch": "Computer Science",
        "target_role": "Python Developer"
    },


    # ========================================================
    # APTITUDE
    # ========================================================

    {
        "section": "Aptitude",
        "topic": "Percentage",
        "question_text": "What is 20% of 250?",
        "option_a": "25",
        "option_b": "40",
        "option_c": "50",
        "option_d": "60",
        "correct_answer": "C",
        "explanation": "20% of 250 = 20/100 × 250 = 50.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Aptitude",
        "topic": "Percentage",
        "question_text": "A number is increased from 200 to 240. What is the percentage increase?",
        "option_a": "10%",
        "option_b": "15%",
        "option_c": "20%",
        "option_d": "25%",
        "correct_answer": "C",
        "explanation": "Increase = 40. Percentage increase = 40/200 × 100 = 20%.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Aptitude",
        "topic": "Profit and Loss",
        "question_text": "An item is bought for ₹500 and sold for ₹600. What is the profit percentage?",
        "option_a": "10%",
        "option_b": "15%",
        "option_c": "20%",
        "option_d": "25%",
        "correct_answer": "C",
        "explanation": "Profit = ₹100. Profit percentage = 100/500 × 100 = 20%.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Aptitude",
        "topic": "Average",
        "question_text": "What is the average of 10, 20, 30, 40 and 50?",
        "option_a": "20",
        "option_b": "25",
        "option_c": "30",
        "option_d": "35",
        "correct_answer": "C",
        "explanation": "Sum = 150 and there are 5 numbers. Average = 150/5 = 30.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Aptitude",
        "topic": "Ratio",
        "question_text": "If the ratio of boys to girls is 2:3 and there are 20 boys, how many girls are there?",
        "option_a": "25",
        "option_b": "30",
        "option_c": "35",
        "option_d": "40",
        "correct_answer": "B",
        "explanation": "2 parts = 20, so 1 part = 10. Therefore 3 parts = 30.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Aptitude",
        "topic": "Time and Work",
        "question_text": "If a person completes a job in 10 days, what fraction of the job is completed in one day?",
        "option_a": "1/5",
        "option_b": "1/10",
        "option_c": "1/20",
        "option_d": "1/2",
        "correct_answer": "B",
        "explanation": "One day's work is 1/10 of the total work.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Aptitude",
        "topic": "Simple Interest",
        "question_text": "What is the simple interest on ₹1000 at 10% per year for 2 years?",
        "option_a": "₹100",
        "option_b": "₹150",
        "option_c": "₹200",
        "option_d": "₹250",
        "correct_answer": "C",
        "explanation": "SI = P × R × T / 100 = 1000 × 10 × 2 / 100 = ₹200.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Aptitude",
        "topic": "Number System",
        "question_text": "Which of the following is a prime number?",
        "option_a": "21",
        "option_b": "27",
        "option_c": "29",
        "option_d": "33",
        "correct_answer": "C",
        "explanation": "29 has only two factors: 1 and 29.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },


    # ========================================================
    # LOGICAL REASONING
    # ========================================================

    {
        "section": "Logical Reasoning",
        "topic": "Number Series",
        "question_text": "Find the next number: 2, 4, 8, 16, ?",
        "option_a": "20",
        "option_b": "24",
        "option_c": "32",
        "option_d": "36",
        "correct_answer": "C",
        "explanation": "Each number is multiplied by 2. Therefore the next number is 32.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Logical Reasoning",
        "topic": "Number Series",
        "question_text": "Find the next number: 3, 6, 12, 24, ?",
        "option_a": "36",
        "option_b": "42",
        "option_c": "48",
        "option_d": "54",
        "correct_answer": "C",
        "explanation": "Each number is multiplied by 2.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Logical Reasoning",
        "topic": "Analogy",
        "question_text": "Book is to Reading as Fork is to:",
        "option_a": "Writing",
        "option_b": "Eating",
        "option_c": "Cooking",
        "option_d": "Cutting",
        "correct_answer": "B",
        "explanation": "A book is used for reading, while a fork is commonly used for eating.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Logical Reasoning",
        "topic": "Coding-Decoding",
        "question_text": "If CAT is coded as DBU, how is DOG coded?",
        "option_a": "EPH",
        "option_b": "EPG",
        "option_c": "FOH",
        "option_d": "DPH",
        "correct_answer": "A",
        "explanation": "Each letter is shifted one position forward: D→E, O→P, G→H.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Logical Reasoning",
        "topic": "Direction Sense",
        "question_text": "A person walks 5 km north and then 5 km south. Where is the person relative to the starting point?",
        "option_a": "5 km north",
        "option_b": "5 km south",
        "option_c": "At the starting point",
        "option_d": "10 km north",
        "correct_answer": "C",
        "explanation": "The person travels equal distances in opposite directions and returns to the starting point.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Logical Reasoning",
        "topic": "Odd One Out",
        "question_text": "Which one is different from the others?",
        "option_a": "Apple",
        "option_b": "Mango",
        "option_c": "Carrot",
        "option_d": "Banana",
        "correct_answer": "C",
        "explanation": "Carrot is a vegetable, while the others are fruits.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Logical Reasoning",
        "topic": "Blood Relations",
        "question_text": "A is the brother of B. B is the sister of C. How is A related to C?",
        "option_a": "Brother",
        "option_b": "Sister",
        "option_c": "Father",
        "option_d": "Uncle",
        "correct_answer": "A",
        "explanation": "A and B are siblings, and B and C are siblings. Therefore A is C's brother.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },


    # ========================================================
    # COMMUNICATION
    # ========================================================

    {
        "section": "Communication",
        "topic": "Grammar",
        "question_text": "Choose the grammatically correct sentence.",
        "option_a": "He go to college every day.",
        "option_b": "He goes to college every day.",
        "option_c": "He going to college every day.",
        "option_d": "He gone to college every day.",
        "correct_answer": "B",
        "explanation": "With the singular subject 'He', the simple present verb is 'goes'.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Communication",
        "topic": "Vocabulary",
        "question_text": "Choose the synonym of 'rapid'.",
        "option_a": "Slow",
        "option_b": "Quick",
        "option_c": "Weak",
        "option_d": "Late",
        "correct_answer": "B",
        "explanation": "Rapid means happening quickly or at a fast rate.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Communication",
        "topic": "Vocabulary",
        "question_text": "Choose the antonym of 'ancient'.",
        "option_a": "Old",
        "option_b": "Historic",
        "option_c": "Modern",
        "option_d": "Traditional",
        "correct_answer": "C",
        "explanation": "Modern is the opposite of ancient.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Communication",
        "topic": "Sentence Correction",
        "question_text": "Choose the correct sentence.",
        "option_a": "She have completed the project.",
        "option_b": "She has completed the project.",
        "option_c": "She having completed the project.",
        "option_d": "She complete the project.",
        "correct_answer": "B",
        "explanation": "The singular subject 'She' takes 'has' in the present perfect tense.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Communication",
        "topic": "Professional Communication",
        "question_text": "Which is most appropriate during a job interview?",
        "option_a": "Avoid eye contact completely.",
        "option_b": "Interrupt the interviewer frequently.",
        "option_c": "Listen carefully and answer clearly.",
        "option_d": "Use informal slang throughout.",
        "correct_answer": "C",
        "explanation": "Active listening and clear, professional answers are important interview skills.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },


    # ========================================================
    # CODING CONCEPTS
    # ========================================================

    {
        "section": "Coding Concepts",
        "topic": "Programming Basics",
        "question_text": "What is the purpose of a loop?",
        "option_a": "To repeat a block of code",
        "option_b": "To permanently delete code",
        "option_c": "To create a database",
        "option_d": "To compile hardware",
        "correct_answer": "A",
        "explanation": "Loops execute a block of code repeatedly while a condition is satisfied or for a specified number of iterations.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Coding Concepts",
        "topic": "Arrays",
        "question_text": "What is commonly used to access an array element?",
        "option_a": "Index",
        "option_b": "Pointer only",
        "option_c": "Keyword",
        "option_d": "Package",
        "correct_answer": "A",
        "explanation": "Array elements are accessed using an index.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Coding Concepts",
        "topic": "Functions",
        "question_text": "What is the main purpose of a function?",
        "option_a": "To organize reusable code",
        "option_b": "To delete variables",
        "option_c": "To shut down a computer",
        "option_d": "To create hardware",
        "correct_answer": "A",
        "explanation": "Functions group reusable logic into a named unit.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Coding Concepts",
        "topic": "Algorithms",
        "question_text": "Which algorithm is commonly used to sort elements by repeatedly selecting the minimum element?",
        "option_a": "Bubble Sort",
        "option_b": "Selection Sort",
        "option_c": "Binary Search",
        "option_d": "DFS",
        "correct_answer": "B",
        "explanation": "Selection Sort repeatedly selects the smallest remaining element and places it in the correct position.",
        "difficulty": "Medium",
        "branch": None,
        "target_role": None
    },

    {
        "section": "Coding Concepts",
        "topic": "Complexity",
        "question_text": "What is the worst-case time complexity of linear search?",
        "option_a": "O(1)",
        "option_b": "O(log n)",
        "option_c": "O(n)",
        "option_d": "O(n²)",
        "correct_answer": "C",
        "explanation": "Linear search may need to examine every element, giving O(n) worst-case complexity.",
        "difficulty": "Easy",
        "branch": None,
        "target_role": None
    }

]


# ============================================================
# INSERT QUESTIONS
# ============================================================

def seed_questions():

    connection = get_connection()
    cursor = connection.cursor()

    inserted = 0
    skipped = 0

    for question in QUESTIONS:

        # Prevent duplicate questions
        cursor.execute(
            """
            SELECT id
            FROM questions
            WHERE question_text = ?
            """,
            (question["question_text"],)
        )

        existing = cursor.fetchone()

        if existing:

            skipped += 1
            continue

        cursor.execute(
            """
            INSERT INTO questions
            (
                section,
                topic,
                question_text,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer,
                explanation,
                difficulty,
                branch,
                target_role
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                question["section"],
                question["topic"],
                question["question_text"],
                question["option_a"],
                question["option_b"],
                question["option_c"],
                question["option_d"],
                question["correct_answer"],
                question["explanation"],
                question["difficulty"],
                question["branch"],
                question["target_role"]
            )
        )

        inserted += 1

    connection.commit()
    connection.close()

    print("=" * 60)
    print("CareerPredict Question Bank")
    print("=" * 60)
    print(f"Questions inserted : {inserted}")
    print(f"Questions skipped  : {skipped}")
    print(f"Total provided     : {len(QUESTIONS)}")
    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    seed_questions()