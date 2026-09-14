import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE = BASE_DIR / 'data' / 'careerpredict.db'

# 150 general questions: 30 per assessment section.
# They are inserted only when the exact question text is not already present.

def q(section, topic, difficulty, text, a, b, c, d, correct, explanation):
    return (section, topic, difficulty, text, a, b, c, d, correct, explanation)

Q = [
# ---------------- Technical (30) ----------------
q('Technical','Programming Fundamentals','Easy','Which data structure follows LIFO order?','Queue','Stack','Array','Tree','B','A stack removes the most recently added item first.'),
q('Technical','Programming Fundamentals','Easy','Which keyword exits a loop immediately in Java?','continue','break','return','skip','B','break terminates the current loop.'),
q('Technical','Programming Fundamentals','Easy','What is the index of the first element of a Java array?','0','1','-1','Depends on array size','A','Java arrays are zero-indexed.'),
q('Technical','Programming Fundamentals','Easy','Which OOP concept hides internal implementation details?','Inheritance','Encapsulation','Polymorphism','Overloading','B','Encapsulation controls access to an object\'s internal state and implementation.'),
q('Technical','Programming Fundamentals','Easy','Which Java type stores true or false?','int','boolean','char','double','B','boolean represents logical true or false values.'),
q('Technical','Data Structures','Medium','Which data structure is typically used for BFS?','Stack','Queue','Heap','Hash table','B','Breadth-first search processes vertices level by level using a queue.'),
q('Technical','Data Structures','Medium','Average lookup time in a well-distributed hash table is:','O(n)','O(log n)','O(1)','O(n log n)','C','Expected hash-table lookup is O(1) under normal assumptions.'),
q('Technical','Data Structures','Medium','Which structure is best for implementing recursion explicitly?','Queue','Stack','Graph','Heap','B','Function calls use stack-like behavior, so an explicit stack can model recursion.'),
q('Technical','Data Structures','Medium','In a binary search tree, values in the left subtree are normally:','Greater than the root','Less than the root','Equal to every node','Random','B','BST ordering places smaller keys in the left subtree.'),
q('Technical','Data Structures','Medium','Which structure gives efficient priority-based removal?','Priority queue','Linked list','Array only','Set','A','A priority queue is designed to access the highest- or lowest-priority item efficiently.'),
q('Technical','Algorithms','Easy','Binary search requires the data to be:','Encrypted','Sorted','Duplicated','Hashed','B','Binary search relies on sorted ordering to discard half the search space.'),
q('Technical','Algorithms','Medium','What is the worst-case time complexity of merge sort?','O(n)','O(log n)','O(n log n)','O(n²)','C','Merge sort runs in O(n log n) time in the worst case.'),
q('Technical','Algorithms','Medium','Which algorithm finds shortest paths with non-negative edge weights?','Dijkstra','DFS','Bubble sort','Kruskal','A','Dijkstra solves single-source shortest paths when edge weights are non-negative.'),
q('Technical','Algorithms','Medium','What is the complexity of traversing all vertices and edges with adjacency lists?','O(V+E)','O(VE)','O(V²E)','O(log V)','A','A complete graph traversal visits each vertex and edge a constant number of times.'),
q('Technical','Algorithms','Medium','Which sorting algorithm is generally stable?','Heap sort','Merge sort','Selection sort','Quick sort always','B','Standard merge sort can be implemented as a stable sorting algorithm.'),
q('Technical','Databases','Easy','Which SQL command retrieves rows?','SELECT','INSERT','UPDATE','DELETE','A','SELECT retrieves data from database tables.'),
q('Technical','Databases','Easy','A primary key must be:','Nullable and duplicated','Unique and non-null','Only numeric','A foreign key','B','A primary key uniquely identifies each row and cannot be NULL.'),
q('Technical','Databases','Medium','Which normal form removes partial dependency on part of a composite key?','1NF','2NF','3NF','BCNF only','B','Second normal form removes partial dependencies.'),
q('Technical','Databases','Medium','Which SQL clause filters grouped results?','WHERE','ORDER BY','HAVING','LIMIT','C','HAVING filters groups after aggregation.'),
q('Technical','Databases','Medium','Which JOIN returns matching rows from both tables?','FULL JOIN','INNER JOIN','CROSS JOIN','SELF JOIN only','B','INNER JOIN returns rows satisfying the join condition in both tables.'),
q('Technical','Operating Systems','Easy','Which component manages processes and hardware resources?','Compiler','Operating system','Browser','Text editor','B','The operating system manages system resources and provides services to programs.'),
q('Technical','Operating Systems','Medium','Which scheduling algorithm uses a fixed time quantum?','Round Robin','FCFS','SJF','FIFO cache','A','Round Robin gives each ready process a time slice.'),
q('Technical','Operating Systems','Medium','Deadlock requires how many Coffman conditions?','2','3','4','5','C','There are four necessary Coffman conditions for deadlock.'),
q('Technical','Operating Systems','Medium','Virtual memory primarily allows:','Only faster CPUs','Programs to use an address space larger than physical RAM','Removal of all storage','No page faults','B','Virtual memory maps virtual addresses to physical memory and can use secondary storage.'),
q('Technical','Computer Networks','Easy','Which protocol is connection-oriented?','UDP','TCP','IP','DNS','B','TCP establishes a connection and provides reliable ordered delivery.'),
q('Technical','Computer Networks','Easy','Which device forwards packets between different networks?','Switch','Router','Repeater','Keyboard','B','Routers forward packets between networks.'),
q('Technical','Computer Networks','Medium','Which OSI layer handles routing?','Physical','Data Link','Network','Presentation','C','Routing is primarily a Network-layer function.'),
q('Technical','Computer Networks','Medium','What does DNS primarily translate?','MAC to RAM','Domain names to IP addresses','Ports to CPUs','Files to folders','B','DNS resolves human-readable domain names to IP addresses.'),
q('Technical','Software Engineering','Easy','What is version control used for?','Only compiling code','Tracking changes to files and collaborating','Deleting bugs automatically','Increasing RAM','B','Version control records changes and supports collaboration and rollback.'),
q('Technical','Software Engineering','Medium','Which testing level focuses on individual functions or units?','Unit testing','System testing','Acceptance testing','Load testing','A','Unit testing verifies small isolated components such as functions or classes.'),

# ---------------- Aptitude (30) ----------------
q('Aptitude','Percentages','Easy','What is 20% of 250?','25','40','50','60','C','20% of 250 is 50.'),
q('Aptitude','Percentages','Easy','A price of 800 is increased by 10%. What is the new price?','810','860','880','900','C','10% of 800 is 80, so the new price is 880.'),
q('Aptitude','Percentages','Medium','A number is increased from 120 to 150. What is the percentage increase?','20%','25%','30%','35%','B','The increase is 30; 30/120 × 100 = 25%.'),
q('Aptitude','Profit and Loss','Easy','An item costs 500 and is sold for 600. Profit percentage is:','10%','15%','20%','25%','C','Profit is 100, and 100/500 × 100 = 20%.'),
q('Aptitude','Profit and Loss','Medium','An item marked 1000 is sold at 15% discount. Selling price is:','750','800','850','900','C','15% of 1000 is 150, leaving 850.'),
q('Aptitude','Ratio','Easy','The ratio 2:3 has a total of 25. The first part is:','8','10','12','15','B','Five equal parts total 25, so each is 5 and the first part is 10.'),
q('Aptitude','Ratio','Medium','If A:B = 3:5 and B:C = 10:7, then A:C is:','3:7','6:7','7:6','5:7','B','Scale 3:5 to 6:10, so A:C = 6:7.'),
q('Aptitude','Averages','Easy','Average of 10, 20 and 30 is:','15','20','25','30','B','Their sum is 60 and 60/3 = 20.'),
q('Aptitude','Averages','Medium','Average of five numbers is 18. Their sum is:','72','80','90','100','C','Sum = average × count = 18 × 5 = 90.'),
q('Aptitude','Time and Work','Easy','If a worker completes a job in 10 days, the daily work rate is:','1/5','1/10','10','100','B','One complete job divided over 10 days gives 1/10 per day.'),
q('Aptitude','Time and Work','Medium','A can finish a job in 12 days and B in 6 days. Together they take:','3 days','4 days','6 days','9 days','B','Combined rate is 1/12 + 1/6 = 1/4, so the time is 4 days.'),
q('Aptitude','Time Speed Distance','Easy','A car travels 120 km in 3 hours. Speed is:','30 km/h','40 km/h','50 km/h','60 km/h','B','Speed = distance/time = 120/3 = 40 km/h.'),
q('Aptitude','Time Speed Distance','Medium','At 60 km/h, how far does a vehicle travel in 2.5 hours?','120 km','150 km','180 km','200 km','B','Distance = speed × time = 60 × 2.5 = 150 km.'),
q('Aptitude','Simple Interest','Easy','Simple interest on 1000 at 10% per year for 2 years is:','100','150','200','220','C','SI = PRT/100 = 1000×10×2/100 = 200.'),
q('Aptitude','Simple Interest','Medium','If simple interest is 240 on principal 1200 at 10% per year, time is:','1 year','2 years','3 years','4 years','B','240 = 1200×10×T/100, so T = 2.'),
q('Aptitude','Number System','Easy','Which number is prime?','21','29','35','39','B','29 has no positive divisors other than 1 and itself.'),
q('Aptitude','Number System','Easy','What is the remainder when 17 is divided by 5?','1','2','3','4','B','17 = 5×3 + 2.'),
q('Aptitude','Number System','Medium','LCM of 12 and 18 is:','24','30','36','48','C','Prime factors give LCM 2²×3² = 36.'),
q('Aptitude','Probability','Easy','Probability of getting heads on a fair coin is:','0','1/4','1/2','1','C','A fair coin has two equally likely outcomes.'),
q('Aptitude','Probability','Medium','A die is rolled once. Probability of getting an even number is:','1/6','1/3','1/2','2/3','C','There are three even outcomes among six: 2, 4, and 6.'),
q('Aptitude','Algebra','Easy','If x + 7 = 15, x equals:','6','7','8','9','C','Subtracting 7 from both sides gives x = 8.'),
q('Aptitude','Algebra','Medium','If 3x - 5 = 16, x equals:','5','6','7','8','C','3x = 21, so x = 7.'),
q('Aptitude','Data Interpretation','Easy','A student scores 70, 80, 90 and 60. Total is:','280','290','300','310','C','70+80+90+60 = 300.'),
q('Aptitude','Data Interpretation','Medium','If sales rise from 200 units to 260 units, the increase is:','20%','25%','30%','35%','C','Increase is 60; 60/200 × 100 = 30%.'),
q('Aptitude','Mixtures','Medium','A 10-liter solution contains 2 liters of water. Water percentage is:','10%','20%','25%','30%','B','2/10 × 100 = 20%.'),
q('Aptitude','Ages','Easy','A is 5 years older than B. If B is 20, A is:','15','20','25','30','C','20 + 5 = 25.'),
q('Aptitude','Ages','Medium','Father is 3 times son\'s age. Son is 12. Father\'s age is:','24','30','36','42','C','3 × 12 = 36.'),
q('Aptitude','Permutations','Medium','How many ways can 3 distinct books be arranged in a row?','3','6','9','12','B','3! = 6.'),
q('Aptitude','Clocks','Medium','How many degrees does the minute hand move in 30 minutes?','90°','120°','180°','360°','C','The minute hand completes 360° in 60 minutes, so 30 minutes is 180°.'),
q('Aptitude','Logical Quantitative','Medium','If 5 machines make 5 items in 5 minutes, how many items do 10 machines make in 5 minutes at the same rate?','5','10','15','20','B','Each machine makes one item in 5 minutes, so 10 machines make 10 items.'),

# ---------------- Logical Reasoning (30) ----------------
q('Logical Reasoning','Series','Easy','Find the next number: 2, 4, 6, 8, ?','9','10','11','12','B','The sequence increases by 2.'),
q('Logical Reasoning','Series','Easy','Find the next number: 3, 6, 12, 24, ?','36','42','48','54','C','Each term is doubled.'),
q('Logical Reasoning','Series','Medium','Find the next number: 1, 4, 9, 16, ?','20','24','25','30','C','These are consecutive squares: 1², 2², 3², 4², 5².'),
q('Logical Reasoning','Alphabet Series','Easy','Complete: A, C, E, G, ?','H','I','J','K','B','Every second letter is selected.'),
q('Logical Reasoning','Alphabet Series','Medium','Complete: AZ, BY, CX, ?','DW','EV','FU','GT','A','The first letter moves forward while the second moves backward.'),
q('Logical Reasoning','Analogy','Easy','Book is to Reading as Fork is to:','Writing','Eating','Drawing','Sleeping','B','A fork is primarily associated with eating.'),
q('Logical Reasoning','Analogy','Easy','Bird is to Fly as Fish is to:','Run','Swim','Walk','Jump','B','Fish move through water by swimming.'),
q('Logical Reasoning','Classification','Easy','Which does not belong?','Apple','Mango','Carrot','Banana','C','Carrot is a vegetable; the others are fruits.'),
q('Logical Reasoning','Classification','Medium','Which number does not belong?','3','6','9','14','C','3, 6 and 9 are multiples of 3; 14 is not.'),
q('Logical Reasoning','Coding-Decoding','Easy','If CAT is coded as DBU, DOG is coded as:','EPH','EOG','DPH','FPI','A','Each letter is shifted one position forward.'),
q('Logical Reasoning','Coding-Decoding','Medium','If BLUE is coded as 2-12-21-5 using alphabet positions, RED is:','18-5-4','17-5-4','18-4-5','19-5-4','A','R=18, E=5, D=4.'),
q('Logical Reasoning','Blood Relations','Easy','Ravi is the brother of Sita. Sita is the mother of Arun. Ravi is Arun\'s:','Father','Brother','Uncle','Grandfather','C','Mother\'s brother is maternal uncle.'),
q('Logical Reasoning','Blood Relations','Medium','A is B\'s sister. B is C\'s father. A is C\'s:','Mother','Aunt','Sister','Daughter','B','A is the sister of C\'s father, so she is C\'s aunt.'),
q('Logical Reasoning','Direction Sense','Easy','A person walks north, then turns right. Which direction is he facing?','West','South','East','North','C','A right turn from north points east.'),
q('Logical Reasoning','Direction Sense','Medium','A person faces east and turns left twice. He faces:','North','South','West','East','C','East → north → west.'),
q('Logical Reasoning','Syllogism','Easy','All programmers are logical. Ravi is a programmer. Therefore Ravi is:','Logical','Not logical','A manager','Unknown','A','Ravi belongs to the set of programmers, which is contained in logical people.'),
q('Logical Reasoning','Syllogism','Medium','All cats are animals. Some animals are black. Which conclusion must be true?','All cats are black','Some cats are black','All black things are cats','Cats are animals','D','The first statement directly establishes that every cat is an animal.'),
q('Logical Reasoning','Statement Assumption','Medium','Statement: Use helmets to reduce head injuries. Assumption:','Helmets can reduce injury risk','Helmets increase speed','Everyone dislikes helmets','Roads are always empty','A','The recommendation assumes helmets provide protective benefit.'),
q('Logical Reasoning','Odd One Out','Easy','Which is different?','Square','Triangle','Circle','Rectangle','C','Circle has no straight sides; the others are polygons.'),
q('Logical Reasoning','Ordering','Easy','P is taller than Q. Q is taller than R. Who is shortest?','P','Q','R','Cannot say','C','The ordering is P > Q > R.'),
q('Logical Reasoning','Ordering','Medium','A is older than B, B older than C, and D older than A. Who is oldest?','A','B','C','D','D','The order is D > A > B > C.'),
q('Logical Reasoning','Calendar','Easy','If today is Monday, what day is it after 3 days?','Tuesday','Wednesday','Thursday','Friday','C','Three days after Monday is Thursday.'),
q('Logical Reasoning','Calendar','Medium','If January 1 is Friday in a non-leap year, January 8 is:','Thursday','Friday','Saturday','Sunday','B','Seven days later is the same weekday.'),
q('Logical Reasoning','Seating Arrangement','Medium','Five people sit in a row. A is left of B and C is right of B. Which order is possible?','C-B-A','A-B-C','B-C-A','A-C-B','B','A-B-C satisfies A left of B and C right of B.'),
q('Logical Reasoning','Logical Puzzle','Medium','Three boxes are labeled Apples, Oranges and Mixed, but all labels are wrong. From which box should you draw one fruit first?','Apples','Oranges','Mixed','Any box','C','The box labeled Mixed cannot be mixed, so one fruit identifies its actual single-fruit type.'),
q('Logical Reasoning','Pattern','Medium','What comes next: 5, 10, 20, 40, ?','60','70','80','90','C','Each term doubles.'),
q('Logical Reasoning','Venn Logic','Medium','If all doctors are graduates and some graduates are researchers, which must be true?','All doctors are graduates','All doctors are researchers','All researchers are doctors','No graduate is a doctor','A','The first statement directly implies all doctors are graduates.'),
q('Logical Reasoning','Truth and Lie','Medium','A person says, I always lie. What is the logical issue?','It creates a contradiction under ordinary truth-value logic','It proves he is honest','It proves he is a doctor','There is no issue','A','The statement creates the classic liar paradox.'),
q('Logical Reasoning','Missing Number','Medium','2, 3, 5, 8, 13, ?','18','20','21','24','C','Each term is the sum of the previous two.'),
q('Logical Reasoning','Data Sufficiency','Medium','Is x positive? Statement 1: x² = 9. Statement 2: x > 0. Which is sufficient?','Statement 1 only','Statement 2 only','Both together only','Neither','B','Statement 2 directly establishes that x is positive.'),

# ---------------- Communication (30) ----------------
q('Communication','Interview Communication','Easy','Which is the most professional interview opening?','Hey, what\'s up?','Good morning. Thank you for the opportunity.','I need this job.','What\'s the salary?','B','A polite greeting and appreciation are professional.'),
q('Communication','Grammar','Easy','Choose the correct sentence.','She have completed the task.','She has completed the task.','She completed has the task.','She having completed the task.','B','The singular subject she takes has in the present perfect.'),
q('Communication','Interview Communication','Easy','What should you do if you do not know an interview answer?','Guess confidently','Ignore the question','Be honest and explain how you would find the answer','Leave immediately','C','Honesty combined with a problem-solving approach demonstrates professionalism.'),
q('Communication','Teamwork','Easy','Which skill is important for effective teamwork?','Refusing feedback','Active listening','Avoiding communication','Working alone','B','Active listening improves understanding and collaboration.'),
q('Communication','Presentation','Easy','If the audience looks confused, you should:','Speak faster','Ignore them','Pause and clarify','End immediately','C','Clarifying the point helps restore audience understanding.'),
q('Communication','Grammar','Easy','Choose the correct sentence.','They is ready.','They are ready.','They am ready.','They be ready.','B','They takes the plural verb are.'),
q('Communication','Vocabulary','Easy','The word concise most nearly means:','Very long','Brief and clear','Unrelated','Difficult to hear','B','Concise communication expresses ideas briefly and clearly.'),
q('Communication','Vocabulary','Medium','Collaborate means to:','Compete alone','Work together','Avoid work','Delay a task','B','Collaboration means working jointly toward a goal.'),
q('Communication','Email Etiquette','Easy','Which subject line is most professional?','HEY!!!','Need job','Application for Software Developer Internship','Read this now','C','A specific and descriptive subject line is professional.'),
q('Communication','Email Etiquette','Medium','What should a professional email usually contain?','Only emojis','Greeting, clear purpose, and appropriate closing','No subject','All capital letters','B','Professional emails should be structured, clear, and respectful.'),
q('Communication','Interview Communication','Medium','When asked Tell me about yourself, the best approach is to:','Tell your entire life story','Give a concise professional summary relevant to the role','Say only your name','Discuss salary first','B','A focused summary should connect education, skills, projects, and goals to the role.'),
q('Communication','Interview Communication','Medium','How should you respond to constructive criticism?','Become defensive','Listen, understand it, and improve','Ignore it','Blame someone else','B','Constructive feedback is useful when received professionally and acted upon.'),
q('Communication','Presentation','Medium','A strong presentation should generally:','Have a clear structure','Contain every detail possible','Use unreadable text','Avoid examples','A','A clear introduction, body, and conclusion improve comprehension.'),
q('Communication','Grammar','Easy','Choose the correct sentence.','He don\'t know.','He doesn\'t know.','He doesn\'t knows.','He not know.','B','Third-person singular present uses does not with the base verb.'),
q('Communication','Grammar','Medium','Choose the correct sentence.','Neither the manager nor the employees was ready.','Neither the manager nor the employees were ready.','Neither manager nor employees is ready.','Neither were manager ready.','B','With neither nor, the verb generally agrees with the nearer plural subject employees.'),
q('Communication','Vocabulary','Medium','The opposite of expand is:','Increase','Extend','Contract','Improve','C','Contract means to become smaller or reduce in size.'),
q('Communication','Listening','Easy','Active listening includes:','Interrupting frequently','Paying attention and clarifying when needed','Checking your phone','Planning your reply without listening','B','Active listening requires attention and clarification.'),
q('Communication','Conflict Resolution','Medium','Two teammates disagree about an approach. What is best?','Choose randomly','Discuss evidence and seek a shared solution','Stop communicating','Escalate immediately without discussion','B','Evidence-based discussion and collaboration are constructive.'),
q('Communication','Workplace Communication','Easy','If you will miss a deadline, you should:','Say nothing','Inform the relevant person early and propose a revised plan','Disappear','Blame the team','B','Early communication allows the team to adjust plans.'),
q('Communication','Interview Communication','Medium','What is a good way to answer a behavioral question?','Use a specific example','Give no details','Change the subject','Use only one-word answers','A','Specific examples demonstrate real behavior and results.'),
q('Communication','Grammar','Easy','Choose the correct spelling.','Accomodation','Accommodation','Acommodation','Accommadation','B','The standard spelling is accommodation.'),
q('Communication','Vocabulary','Easy','Reliable most nearly means:','Dependable','Expensive','Fast only','Creative only','A','Reliable means dependable or consistently trustworthy.'),
q('Communication','Professional Etiquette','Easy','During an online interview, you should:','Check your phone constantly','Test your audio and video beforehand','Join without preparation','Keep unrelated apps visible','B','Testing equipment beforehand reduces technical interruptions.'),
q('Communication','Professional Etiquette','Medium','If you disagree with a manager, a professional response is to:','Insult them','Respectfully explain your reasoning and evidence','Refuse all work','Complain publicly','B','Respectful disagreement supported by evidence is appropriate.'),
q('Communication','Communication Strategy','Medium','When explaining a technical concept to a non-technical person, you should:','Use unexplained jargon','Use simple language and relevant examples','Speak as quickly as possible','Avoid checking understanding','B','Plain language and examples improve accessibility.'),
q('Communication','Grammar','Medium','Choose the correct sentence.','The team have finished its work.','The team has finished its work.','The team has finish its work.','The team finishing work.','B','In standard singular collective usage, team has is correct.'),
q('Communication','Email Etiquette','Easy','Before sending a professional email, you should:','Review recipient, subject, content, and attachments','Send immediately','Use only abbreviations','Write everything in capitals','A','A final review prevents common communication errors.'),
q('Communication','Interview Communication','Easy','What is a good response when asked why you want the role?','Because I need money','Connect your skills and interests to the role','I don\'t know','Any answer is fine','B','A role-focused answer demonstrates motivation and fit.'),
q('Communication','Presentation','Medium','What is the purpose of a conclusion in a presentation?','Introduce unrelated information','Reinforce the main message','Add random jokes only','Start a new topic','B','A conclusion summarizes and reinforces the key message.'),
q('Communication','Teamwork','Medium','A teammate is struggling with a task. A good response is to:','Ignore them','Offer help while respecting responsibilities','Take all their work without discussion','Criticize them publicly','B','Supportive collaboration helps the team while preserving accountability.'),

# ---------------- Coding Concepts (30) ----------------
q('Coding Concepts','Algorithms','Easy','What is the purpose of a loop?','To repeat a block of code','To permanently delete code','To create a database','To compile hardware','A','Loops repeat statements while a condition or iteration rule is satisfied.'),
q('Coding Concepts','Algorithms','Easy','Which algorithm searches a sorted array by repeatedly checking the middle?','Linear search','Binary search','Bubble sort','DFS','B','Binary search halves the search range at each step.'),
q('Coding Concepts','Algorithms','Medium','What is the average-case time complexity of searching a value in a hash table?','O(n²)','O(n)','O(1)','O(log n)','C','Expected hash-table lookup is O(1) with a good hash function and load factor.'),
q('Coding Concepts','Algorithms','Medium','Which algorithm is used to find a minimum spanning tree?','Kruskal\'s algorithm','Binary search','BFS only','Insertion sort','A','Kruskal\'s algorithm constructs a minimum spanning tree by selecting safe edges.'),
q('Coding Concepts','Algorithms','Easy','Which data structure is commonly used by DFS?','Queue','Stack','Heap','Hash table','B','DFS uses a stack explicitly or through recursion.'),
q('Coding Concepts','Complexity','Medium','What is the time complexity of a single loop running n times?','O(1)','O(log n)','O(n)','O(n²)','C','One iteration per element gives linear time.'),
q('Coding Concepts','Complexity','Medium','Two nested loops each running n times usually give:','O(n)','O(log n)','O(n²)','O(2n)','C','The inner loop runs n times for each of n outer iterations.'),
q('Coding Concepts','Recursion','Easy','What must a recursive function normally have to stop recursion?','A base case','A database','A compiler','A network','A','The base case prevents infinite recursive calls.'),
q('Coding Concepts','Recursion','Medium','If a recursive algorithm makes one recursive call with n-1, recursion depth is typically:','O(1)','O(log n)','O(n)','O(n²)','C','Each call reduces n by one, producing about n stack frames.'),
q('Coding Concepts','Arrays','Easy','Which property makes array indexing fast?','Elements are stored with predictable positions','Arrays are always sorted','Arrays never use memory','Arrays require hashing','A','Direct address calculation allows constant-time indexed access.'),
q('Coding Concepts','Linked Lists','Medium','In a singly linked list, each node normally stores:','Only a value','A value and a link to the next node','Only an index','A database connection','B','A singly linked-list node contains data and a next reference.'),
q('Coding Concepts','Stacks','Easy','Which operation removes the top stack element?','enqueue','push','pop','peek only','C','pop removes the top element.'),
q('Coding Concepts','Queues','Easy','Which operation adds an element to a queue?','dequeue','enqueue','pop','peek','B','enqueue adds an item to the rear of a queue.'),
q('Coding Concepts','Trees','Medium','Which traversal of a binary search tree produces sorted keys?','Preorder','Postorder','Inorder','Level order always','C','Inorder traversal visits left subtree, root, then right subtree, yielding sorted keys in a BST.'),
q('Coding Concepts','Graphs','Easy','A graph consists primarily of:','Rows and columns only','Vertices and edges','Functions and classes','Files and folders','B','Graphs model relationships using vertices connected by edges.'),
q('Coding Concepts','Graphs','Medium','BFS is particularly useful for shortest paths in:','Unweighted graphs','Any graph with negative cycles','Only trees with weights','Databases','A','BFS finds shortest path lengths in unweighted graphs.'),
q('Coding Concepts','Sorting','Easy','Which sorting algorithm repeatedly swaps adjacent out-of-order elements?','Bubble sort','Merge sort','Heap sort','Radix sort','A','Bubble sort compares adjacent elements and swaps them when needed.'),
q('Coding Concepts','Sorting','Medium','Worst-case time complexity of quicksort with poor pivot choices can be:','O(log n)','O(n)','O(n log n)','O(n²)','D','Repeatedly choosing an extreme pivot can create highly unbalanced partitions.'),
q('Coding Concepts','Searching','Easy','Linear search has worst-case complexity:','O(1)','O(log n)','O(n)','O(n²)','C','In the worst case every element is inspected.'),
q('Coding Concepts','Searching','Medium','Binary search has worst-case complexity on a sorted array of:','O(n)','O(log n)','O(n log n)','O(n²)','B','Each comparison approximately halves the remaining search interval.'),
q('Coding Concepts','OOP','Easy','Which OOP feature allows one interface to have multiple implementations?','Polymorphism','Compilation','Parsing','Indexing','A','Polymorphism allows the same interface or operation to behave differently for different types.'),
q('Coding Concepts','OOP','Easy','Method overloading means:','Same method name with different parameter lists','Replacing a database','Deleting a class','Using only one method','A','Overloaded methods share a name but differ in parameter lists.'),
q('Coding Concepts','OOP','Medium','Method overriding occurs when:','A subclass provides a compatible implementation of an inherited method','Two unrelated variables share a name','A loop repeats','A table is normalized','A','Overriding lets a subclass redefine inherited behavior.'),
q('Coding Concepts','Java','Easy','Which keyword creates an object in Java?','make','new','object','create','B','The new keyword allocates and initializes an object.'),
q('Coding Concepts','Java','Easy','Which Java collection does not allow duplicate elements?','List','Set','ArrayList only','Queue always','B','Set is designed to contain unique elements.'),
q('Coding Concepts','Java','Medium','Which exception is commonly thrown for an invalid array index in Java?','IOException','ArrayIndexOutOfBoundsException','SQLException','ClassNotFoundException','B','Java throws ArrayIndexOutOfBoundsException for an invalid array index.'),
q('Coding Concepts','Python','Easy','Which symbol starts a comment in Python?','//','#','<!--','--','B','Python uses # for single-line comments.'),
q('Coding Concepts','Python','Medium','Which Python structure stores key-value pairs?','List','Tuple','Dictionary','Set only','C','A dictionary maps keys to values.'),
q('Coding Concepts','C++','Easy','Which operator is used for dynamic allocation in C++?','malloc only','new','alloc','create','B','C++ uses new for dynamic allocation.'),
q('Coding Concepts','JavaScript','Easy','Which keyword declares a block-scoped variable that can be reassigned?','const','let','fixed','varonly','B','let declares a block-scoped variable that can be reassigned.'),
]

if len(Q) != 150:
    raise RuntimeError(f'Expected 150 questions, found {len(Q)}')


def main():
    if not DATABASE.exists():
        raise FileNotFoundError(f'Database not found: {DATABASE}')

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    inserted = 0
    skipped = 0

    for row in Q:
        cur.execute('SELECT id FROM questions WHERE question_text = ? LIMIT 1', (row[3],))
        if cur.fetchone():
            skipped += 1
            continue

        cur.execute('''
            INSERT INTO questions
            (section, topic, difficulty, question_text,
             option_a, option_b, option_c, option_d,
             correct_answer, explanation, branch, target_role, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, 1)
        ''', row)
        inserted += 1

    con.commit()

    print('\nQuestion bank summary:')
    cur.execute('''
        SELECT section, COUNT(*)
        FROM questions
        WHERE is_active = 1
        GROUP BY section
        ORDER BY section
    ''')
    for section, count in cur.fetchall():
        print(f'  {section}: {count}')

    print(f'\nInserted: {inserted}')
    print(f'Already present: {skipped}')
    print('Question bank expansion completed successfully.')
    con.close()


if __name__ == '__main__':
    main()
