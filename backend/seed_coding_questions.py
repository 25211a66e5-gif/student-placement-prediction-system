from database import get_connection
import json

QUESTIONS = [
("Sum of N Numbers","Basics","EASY","Read N integers and print their sum.","First line: N. Second line: N integers.","Print the sum.","5\n1 2 3 4 5\n","15"),
("Count Even Numbers","Arrays","EASY","Count how many of the N integers are even.","First line: N. Second line: N integers.","Print the count of even integers.","6\n1 2 4 7 8 9\n","3"),
("Find Minimum","Arrays","EASY","Find the smallest integer in a list.","First line: N. Second line: N integers.","Print the minimum integer.","5\n8 3 11 2 6\n","2"),
("Reverse a Number","Numbers","EASY","Reverse the digits of a positive integer.","One integer N.","Print the reversed number.","12045\n","50421"),
("Palindrome Number","Numbers","EASY","Check whether a number reads the same forwards and backwards.","One integer N.","Print YES if it is a palindrome, otherwise NO.","1221\n","YES"),
("Count Digits","Numbers","EASY","Count the number of digits in a non-negative integer.","One integer N.","Print the number of digits.","98765\n","5"),
("Sum of Digits","Numbers","EASY","Find the sum of all digits of a non-negative integer.","One integer N.","Print the digit sum.","5832\n","18"),
("Largest of Three","Conditions","EASY","Find the largest of three integers.","Three integers on one line.","Print the largest integer.","12 7 19\n","19"),
("Second Largest","Arrays","EASY","Print the second largest distinct value in the list.","First line: N (N >= 2). Second line: N integers with at least two distinct values.","Print the second largest distinct integer.","6\n10 4 8 10 6 9\n","9"),
("Count Vowels","Strings","EASY","Count vowels in a lowercase English string. Vowels are a,e,i,o,u.","One lowercase string without spaces.","Print the vowel count.","placement\n","3"),
("Reverse String","Strings","EASY","Reverse a string.","One string without spaces.","Print the reversed string.","career\n","reerac"),
("String Palindrome","Strings","EASY","Check whether a string is a palindrome.","One lowercase string without spaces.","Print YES or NO.","level\n","YES"),
("Count Words","Strings","EASY","Count words separated by single spaces.","One line containing lowercase words separated by spaces.","Print the number of words.","machine learning model\n","3"),
("Character Frequency","Strings","EASY","Count occurrences of the character 'a' in a lowercase string.","One lowercase string without spaces.","Print the count of a.","banana\n","3"),
("Factorial","Numbers","EASY","Calculate N factorial for 0 <= N <= 12.","One integer N.","Print N!.","5\n","120"),
("Fibonacci Term","Numbers","EASY","Print the Nth Fibonacci number using F0=0 and F1=1, for 0 <= N <= 30.","One integer N.","Print the Nth Fibonacci number.","10\n","55"),
("Prime Check","Numbers","MEDIUM","Determine whether an integer greater than 1 is prime.","One integer N.","Print PRIME or NOT PRIME.","29\n","PRIME"),
("GCD of Two Numbers","Numbers","EASY","Find the greatest common divisor of two positive integers.","Two integers A and B.","Print gcd(A,B).","48 18\n","6"),
("LCM of Two Numbers","Numbers","EASY","Find the least common multiple of two positive integers.","Two integers A and B.","Print lcm(A,B).","12 18\n","36"),
("Count Positive Values","Arrays","EASY","Count how many values are greater than zero.","First line: N. Second line: N integers.","Print the count of positive values.","6\n-2 4 0 7 -1 3\n","3"),
("Array Average","Arrays","EASY","Print the average of N integers rounded to exactly two decimal places.","First line: N. Second line: N integers.","Print the average with two decimal places.","4\n2 4 6 8\n","5.00"),
("Sorted Check","Arrays","EASY","Check whether the array is in non-decreasing order.","First line: N. Second line: N integers.","Print YES if sorted, otherwise NO.","5\n1 2 2 4 7\n","YES"),
("Linear Search","Arrays","EASY","Find the first zero-based index of X in an array.","First line: N and X. Second line: N integers. X is guaranteed to occur.","Print the first index of X.","5 7\n3 7 2 7 9\n","1"),
("Count Occurrences","Arrays","EASY","Count how many times X occurs in an array.","First line: N and X. Second line: N integers.","Print the occurrence count.","7 4\n4 1 4 2 4 4 9\n","4"),
("Remove Spaces","Strings","EASY","Remove all spaces from a string containing lowercase letters and spaces.","One line of text.","Print the string without spaces.","data science\n","datascience"),
("Sum of Array Except Maximum","Arrays","MEDIUM","Print the sum of all elements except one occurrence of the maximum value.","First line: N. Second line: N integers.","Print the resulting sum.","5\n2 9 4 9 3\n","18"),
("Unique Elements Count","Arrays","MEDIUM","Count how many distinct integers appear in the array.","First line: N. Second line: N integers.","Print the number of distinct values.","7\n1 2 2 3 1 4 4\n","4"),
("Missing Number","Arrays","MEDIUM","The array contains N-1 distinct numbers from 1 to N. Find the missing number.","First line: N. Second line: N-1 integers.","Print the missing number.","5\n1 2 3 5\n","4"),
("Move Zeros","Arrays","MEDIUM","Move all zeros to the end while preserving the order of non-zero values.","First line: N. Second line: N integers.","Print the resulting array separated by spaces.","6\n0 1 0 3 12 0\n","1 3 12 0 0 0"),
("Frequency of Maximum","Arrays","MEDIUM","Print how many times the maximum value occurs.","First line: N. Second line: N integers.","Print the frequency of the maximum.","7\n5 9 2 9 9 1 9\n","4"),
("Anagram Check","Strings","MEDIUM","Check whether two lowercase strings are anagrams of each other.","Two lowercase strings on separate lines, with no spaces.","Print YES if they are anagrams, otherwise NO.","listen\nsilent\n","YES"),
]


def init_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS coding_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        topic TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        description TEXT NOT NULL,
        input_format TEXT NOT NULL,
        output_format TEXT NOT NULL,
        sample_input TEXT NOT NULL,
        sample_output TEXT NOT NULL,
        hidden_tests TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS coding_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assessment_id INTEGER NOT NULL UNIQUE,
        user_id INTEGER NOT NULL,
        coding_question_id INTEGER NOT NULL,
        language TEXT,
        submitted INTEGER NOT NULL DEFAULT 0,
        score REAL NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (coding_question_id) REFERENCES coding_questions(id) ON DELETE CASCADE
    )""")
    conn.commit()
    cur.execute("SELECT COUNT(*) AS c FROM coding_questions")
    count = cur.fetchone()["c"]
    if count == 0:
        for title, topic, difficulty, desc, inp, out, sample_in, sample_out in QUESTIONS:
            # Hidden cases are stored as input/expected pairs. They are never sent by the question endpoint.
            hidden = build_hidden_tests(title)
            cur.execute("""INSERT INTO coding_questions
                (title, topic, difficulty, description, input_format, output_format,
                 sample_input, sample_output, hidden_tests)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (title, topic, difficulty, desc, inp, out, sample_in, sample_out, json.dumps(hidden)))
        conn.commit()
        print(f"Inserted {len(QUESTIONS)} coding questions.")
    else:
        print(f"Coding question bank already contains {count} questions.")
    conn.close()


def build_hidden_tests(title):
    # Additional tests deliberately differ from the public example.
    cases = {
        "Sum of N Numbers": [("1\n8\n","8"),("4\n10 -2 5 7\n","20")],
        "Count Even Numbers": [("5\n2 5 6 7 10\n","3"),("3\n1 3 5\n","0")],
        "Find Minimum": [("4\n-3 -8 2 5\n","-8"),("1\n42\n","42")],
        "Reverse a Number": [("9001\n","1009"),("7\n","7")],
        "Palindrome Number": [("12345\n","NO"),("7\n","YES")],
        "Count Digits": [("0\n","1"),("42\n","2")],
        "Sum of Digits": [("999\n","27"),("10001\n","2")],
        "Largest of Three": [("-5 -2 -9\n","-2"),("4 4 1\n","4")],
        "Second Largest": [("5\n1 5 3 5 2\n","3"),("4\n-1 -5 -2 -3\n","-2")],
        "Count Vowels": [("hello\n","2"),("rhythm\n","0")],
        "Reverse String": [("hello\n","olleh"),("a\n","a")],
        "String Palindrome": [("coding\n","NO"),("madam\n","YES")],
        "Count Words": [("one two\n","2"),("a b c d\n","4")],
        "Character Frequency": [("apple\n","1"),("bbb\n","0")],
        "Factorial": [("0\n","1"),("7\n","5040")],
        "Fibonacci Term": [("0\n","0"),("15\n","610")],
        "Prime Check": [("2\n","PRIME"),("100\n","NOT PRIME")],
        "GCD of Two Numbers": [("100 25\n","25"),("17 13\n","1")],
        "LCM of Two Numbers": [("4 6\n","12"),("7 3\n","21")],
        "Count Positive Values": [("5\n-1 0 2 3 -4\n","2"),("3\n-1 -2 -3\n","0")],
        "Array Average": [("3\n1 2 4\n","2.33"),("2\n5 6\n","5.50")],
        "Sorted Check": [("4\n4 3 2 1\n","NO"),("1\n9\n","YES")],
        "Linear Search": [("4 5\n1 5 5 2\n","1"),("3 -1\n-1 2 4\n","0")],
        "Count Occurrences": [("5 3\n1 2 3 3 3\n","3"),("4 8\n1 2 3 4\n","0")],
        "Remove Spaces": [("hello world test\n","helloworldtest"),("a b\n","ab")],
        "Sum of Array Except Maximum": [("4\n1 2 3 4\n","6"),("3\n5 5 2\n","7")],
        "Unique Elements Count": [("5\n1 1 1 1 1\n","1"),("4\n1 2 3 4\n","4")],
        "Missing Number": [("6\n1 2 6 4 5\n","3"),("3\n1 2\n","3")],
        "Move Zeros": [("5\n0 0 1 2 0\n","1 2 0 0 0"),("3\n1 2 3\n","1 2 3")],
        "Frequency of Maximum": [("5\n2 8 8 1 8\n","3"),("4\n5 1 5 5\n","3")],
        "Anagram Check": [("triangle\nintegral\n","YES"),("hello\nworld\n","NO")],
    }
    return [{"input": i, "expected": o} for i, o in cases.get(title, [])]


if __name__ == "__main__":
    init_table()
