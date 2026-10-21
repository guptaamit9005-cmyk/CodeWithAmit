import os
from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils import timezone
from accounts.models import UserProfile
from courses.models import CourseCategory, Course, Lesson, Quiz, QuizQuestion, Enrollment
from notes.models import NoteCategory, Note
from live_classes.models import LiveClass, ClassAttendee
from coding_practice.models import ProblemCategory, CodingQuestion, UserQuestionStatus
from roadmaps.models import Roadmap, RoadmapStage, RoadmapTopic, UserRoadmapEnrollment
from notifications.models import Notification

class Command(BaseCommand):
    help = 'Seeds Student Success Hub with rich, production-grade educational data'

    def handle(self, *args, **options):
        self.stdout.write("Starting database seeding for Student Success Hub...")

        # 1. Create Users
        # Superuser / Admin
        admin_user, created = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@studentsuccesshub.org',
            'first_name': 'Sarah',
            'last_name': 'Connor',
            'is_staff': True,
            'is_superuser': True,
        })
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        admin_profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        admin_profile.role = 'admin'
        admin_profile.headline = 'Head of Curriculum & Systems Architect'
        admin_profile.points = 1200
        admin_profile.streak_count = 15
        admin_profile.save()

        # Instructor
        instructor_user, created = User.objects.get_or_create(username='instructor', defaults={
            'email': 'instructor@studentsuccesshub.org',
            'first_name': 'Prof. Alex',
            'last_name': 'Vance',
            'is_staff': True,
        })
        if created:
            instructor_user.set_password('instructor123')
            instructor_user.save()
        inst_profile, _ = UserProfile.objects.get_or_create(user=instructor_user)
        inst_profile.role = 'instructor'
        inst_profile.headline = 'Senior Systems Architect & Algorithms Lecturer'
        inst_profile.points = 850
        inst_profile.streak_count = 12
        inst_profile.save()

        # Student
        student_user, created = User.objects.get_or_create(username='student', defaults={
            'email': 'student@studentsuccesshub.org',
            'first_name': 'Rahul',
            'last_name': 'Sharma',
        })
        if created:
            student_user.set_password('student123')
            student_user.save()
        student_profile, _ = UserProfile.objects.get_or_create(user=student_user)
        student_profile.role = 'student'
        student_profile.headline = 'Computer Science Sophomore | Aspiring SDE'
        student_profile.target_career = 'Full-Stack Developer'
        student_profile.points = 340
        student_profile.streak_count = 7
        student_profile.save()

        self.stdout.write("Created users: admin/admin123, instructor/instructor123, student/student123")

        # 2. Course Categories
        cat_python, _ = CourseCategory.objects.get_or_create(name='Python Mastery', defaults={'icon': 'bi-filetype-py', 'description': 'Modern Python 3, OOP, AsyncIO, and scripting.'})
        cat_cpp, _ = CourseCategory.objects.get_or_create(name='C and C++ Systems', defaults={'icon': 'bi-cpu', 'description': 'Memory management, pointers, STL, and systems programming.'})
        cat_web, _ = CourseCategory.objects.get_or_create(name='Full-Stack Web Development', defaults={'icon': 'bi-globe', 'description': 'HTML5, modern CSS, JavaScript, Django, and REST APIs.'})
        cat_dsa, _ = CourseCategory.objects.get_or_create(name='Data Structures and Algorithms', defaults={'icon': 'bi-diagram-3', 'description': 'Arrays, Trees, Graphs, Dynamic Programming, and complexity analysis.'})
        cat_ml, _ = CourseCategory.objects.get_or_create(name='Machine Learning & Data Science', defaults={'icon': 'bi-robot', 'description': 'NumPy, Pandas, Scikit-learn, Neural Networks, and Deep Learning.'})

        # 3. Courses
        course_dsa, _ = Course.objects.get_or_create(
            title='Data Structures & Algorithms: From Scratch to LeetCode',
            defaults={
                'category': cat_dsa,
                'instructor': instructor_user,
                'difficulty': 'Intermediate',
                'thumbnail_url': 'https://images.unsplash.com/photo-1516116211227-bbc1593fefbe?auto=format&fit=crop&w=800&q=80',
                'short_description': 'Master core data structures, graph traversals, and dynamic programming patterns tested in top tech interviews.',
                'description': """Comprehensive deep-dive into Data Structures and Algorithms designed specifically for computer science students.
                
In this course, we demystify asymptotic time and space complexity (Big-O), implement essential data structures from raw memory (Dynamic Arrays, Linked Lists, Binary Search Trees, Heaps, Hash Tables, and Disjoint Set Unions), and conquer interview-proven algorithms like BFS, DFS, Dijkstra's, Topological Sort, and Dynamic Programming.""",
                'estimated_hours': 24,
                'is_published': True,
                'is_featured': True
            }
        )

        course_web, _ = Course.objects.get_or_create(
            title='Modern Full-Stack Python & Django Masterclass',
            defaults={
                'category': cat_web,
                'instructor': instructor_user,
                'difficulty': 'Beginner',
                'thumbnail_url': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80',
                'short_description': 'Build secure, database-backed web applications with Django, Bootstrap 5, PostgreSQL, and modern REST APIs.',
                'description': """Learn to architect production-ready web platforms from scratch. This course guides you through HTTP protocols, Django models, database migrations, template inheritance, authentication pipelines, form handling, and deploying on cloud infrastructure like Render.""",
                'estimated_hours': 18,
                'is_published': True,
                'is_featured': True
            }
        )

        course_cpp, _ = Course.objects.get_or_create(
            title='C++ Core & Modern Systems Architecture',
            defaults={
                'category': cat_cpp,
                'instructor': instructor_user,
                'difficulty': 'Advanced',
                'thumbnail_url': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80',
                'short_description': 'Master C++20, smart pointers, RAII, memory layouts, cache efficiency, and high-performance competitive programming.',
                'description': """C++ remains the backbone of game engines, operating systems, browsers, and low-latency financial systems. This course covers memory virtualization, stack vs heap allocation, template metaprogramming, and concurrency.""",
                'estimated_hours': 20,
                'is_published': True,
                'is_featured': True
            }
        )

        # 4. Lessons & Quizzes for DSA Course
        l1, _ = Lesson.objects.get_or_create(
            course=course_dsa,
            title='Introduction to Big-O Notation & Asymptotic Complexity',
            defaults={
                'order': 1,
                'duration_minutes': 20,
                'video_url': 'https://www.youtube.com/watch?v=D6xkbGLQesk',
                'is_free_preview': True,
                'content': r"""### Understanding Time and Space Complexity
Asymptotic analysis allows us to measure how an algorithm's execution time and memory footprint scale as the input size $N$ tends towards infinity.

Key Complexity Classes from best to worst:
- **$O(1)$** - Constant Time (Hash map lookups, array index access)
- **$O(\log N)$** - Logarithmic Time (Binary Search)
- **$O(N)$** - Linear Time (Single pass over array)
- **$O(N \log N)$** - Linearithmic Time (Merge Sort, Heap Sort)
- **$O(N^2)$** - Quadratic Time (Nested loops, Bubble Sort)
- **$O(2^N)$** - Exponential Time (Subsets generation)
""",
                'code_snippet': """# Python O(log N) Binary Search Implementation
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1""",
                'code_language': 'python'
            }
        )

        l2, _ = Lesson.objects.get_or_create(
            course=course_dsa,
            title='Two Pointers & Sliding Window Patterns',
            defaults={
                'order': 2,
                'duration_minutes': 25,
                'video_url': 'https://www.youtube.com/watch?v=jNX-X12dC_8',
                'is_free_preview': False,
                'content': """### The Power of Two Pointers
When working on sorted arrays or strings, two pointers can reduce $O(N^2)$ brute-force solutions down to optimal $O(N)$ linear time.

Common variations:
1. **Opposite Ends**: Left pointer at 0, Right pointer at $N-1$ (e.g. Two Sum II, Palindrome verification)
2. **Fast & Slow**: Floyd's Cycle Detection in Linked Lists
3. **Sliding Window**: Dynamic subarray boundaries (e.g. Longest Substring Without Repeating Characters)
""",
                'code_snippet': """def isPalindrome(s: str) -> bool:
    clean = [c.lower() for c in s if c.isalnum()]
    left, right = 0, len(clean) - 1
    while left < right:
        if clean[left] != clean[right]:
            return False
        left += 1
        right -= 1
    return True""",
                'code_language': 'python'
            }
        )

        # Attach Quiz to Lesson 1
        quiz1, _ = Quiz.objects.get_or_create(
            lesson=l1,
            defaults={
                'title': 'Big-O Analysis Checkpoint',
                'description': 'Test your mastery of time complexity rankings and binary search.',
                'passing_score': 70
            }
        )
        QuizQuestion.objects.get_or_create(
            quiz=quiz1,
            question_text='What is the time complexity of searching an element in a balanced Binary Search Tree (BST)?',
            defaults={
                'option_a': 'O(1)',
                'option_b': 'O(log N)',
                'option_c': 'O(N)',
                'option_d': 'O(N log N)',
                'correct_option': 'B',
                'explanation': 'In a balanced binary search tree, half of the remaining nodes are discarded at each step, yielding O(log N) time.'
            }
        )
        QuizQuestion.objects.get_or_create(
            quiz=quiz1,
            question_text='Which complexity class grows fastest as N becomes large?',
            defaults={
                'option_a': 'O(N^2)',
                'option_b': 'O(N log N)',
                'option_c': 'O(2^N)',
                'option_d': 'O(N^3)',
                'correct_option': 'C',
                'explanation': 'O(2^N) is exponential time, which outgrows polynomial complexities (such as N^2 or N^3) for large inputs.'
            }
        )

        # Enroll student in DSA
        Enrollment.objects.get_or_create(user=student_user, course=course_dsa)

        # 5. Notes Library
        note_cat_cs, _ = NoteCategory.objects.get_or_create(name='Core CS Fundamentals', defaults={'icon': 'bi-cpu', 'description': 'OS, DBMS, Computer Networks, and Architecture'})
        note_cat_math, _ = NoteCategory.objects.get_or_create(name='Mathematics & Theory', defaults={'icon': 'bi-calculator', 'description': 'Discrete Math, Graph Theory, and Probability'})

        # Sample PDF content generator
        sample_pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 55 >>\nstream\nBT /F1 24 Tf 100 700 Td (Student Success Hub - OS Notes) ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000214 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n320\n%%EOF"

        note1, created1 = Note.objects.get_or_create(
            title='Operating Systems: Complete Process Scheduling & Memory Management Notes',
            defaults={
                'category': note_cat_cs,
                'subject': 'Operating Systems (CS301)',
                'semester': 'sem_3',
                'programming_language': 'C / C++',
                'description': 'Comprehensive handwritten reference covering CPU Scheduling algorithms (FCFS, SJF, Round Robin), Deadlock Banker Algorithm, Virtual Memory paging, and Semaphore synchronizations with diagrams.',
                'uploader': instructor_user,
                'is_approved': True,
                'is_featured': True,
                'download_count': 1240,
            }
        )
        if created1 or not note1.file:
            note1.file.save('operating_systems_complete_guide.pdf', ContentFile(sample_pdf_content))
            note1.save()

        note2, created2 = Note.objects.get_or_create(
            title='Database Management Systems: SQL, Normalization (1NF to BCNF) & Indexing',
            defaults={
                'category': note_cat_cs,
                'subject': 'DBMS (CS304)',
                'semester': 'sem_4',
                'programming_language': 'SQL / PostgreSQL',
                'description': 'In-depth notes on Relational Algebra, Functional Dependencies, Lossless Joins, ACID properties, Transaction Concurrency with 2-Phase Locking, and B+ Tree Indexing.',
                'uploader': instructor_user,
                'is_approved': True,
                'is_featured': True,
                'download_count': 980,
            }
        )
        if created2 or not note2.file:
            note2.file.save('dbms_normalization_indexing.pdf', ContentFile(sample_pdf_content))
            note2.save()

        # 6. Live Classes (Google Meet Sessions)
        today = timezone.now().date()
        class_live, _ = LiveClass.objects.get_or_create(
            title='Mastering Dynamic Programming Patterns: 1D to 2D DP',
            defaults={
                'description': 'Interactive live session breaking down the 5 dynamic programming patterns tested by FAANG/tier-1 product companies. Live coding in Python and C++ with real-time Q&A.',
                'instructor': instructor_user,
                'scheduled_date': today,
                'start_time': time(18, 30),
                'duration_minutes': 90,
                'google_meet_url': 'https://meet.google.com/abc-defg-hij',
                'status': 'live',
            }
        )
        ClassAttendee.objects.get_or_create(live_class=class_live, user=student_user)

        class_upcoming, _ = LiveClass.objects.get_or_create(
            title='System Design Primer: Designing Scalable URL Shortener & Rate Limiter',
            defaults={
                'description': 'High-level and low-level architecture breakdown: consistent hashing, token bucket algorithm, Redis caching, and database sharding techniques.',
                'instructor': instructor_user,
                'scheduled_date': today + timedelta(days=2),
                'start_time': time(19, 0),
                'duration_minutes': 75,
                'google_meet_url': 'https://meet.google.com/xyz-uvwx-rst',
                'status': 'upcoming',
            }
        )
        ClassAttendee.objects.get_or_create(live_class=class_upcoming, user=student_user)

        # 7. Coding Practice Questions
        pcat_arrays, _ = ProblemCategory.objects.get_or_create(name='Arrays & Hashing', defaults={'icon': 'bi-grid-3x3'})
        pcat_strings, _ = ProblemCategory.objects.get_or_create(name='Two Pointers & Strings', defaults={'icon': 'bi-cursor'})
        pcat_linked_list, _ = ProblemCategory.objects.get_or_create(name='Linked Lists', defaults={'icon': 'bi-link-45deg'})
        pcat_trees, _ = ProblemCategory.objects.get_or_create(name='Trees & Graphs', defaults={'icon': 'bi-diagram-2'})

        q1, _ = CodingQuestion.objects.get_or_create(
            title='Two Sum',
            defaults={
                'category': pcat_arrays,
                'difficulty': 'Easy',
                'description': """Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.""",
                'input_format': 'nums: List[int], target: int',
                'output_format': 'List[int]',
                'constraints': """2 <= nums.length <= 10^4
-10^9 <= nums[i] <= 10^9
-10^9 <= target <= 10^9
Only one valid answer exists.""",
                'example_1_input': 'nums = [2,7,11,15], target = 9',
                'example_1_output': '[0,1]',
                'example_1_explanation': 'Because nums[0] + nums[1] == 9, we return [0, 1].',
                'example_2_input': 'nums = [3,2,4], target = 6',
                'example_2_output': '[1,2]',
                'hints': """A really brute force way would be to search for all possible pairs, but that takes O(N^2) time.
Can we use a hash map to look up if (target - current_value) already exists in O(1) time?""",
                'leetcode_url': 'https://leetcode.com/problems/two-sum/',
                'gfg_url': 'https://www.geeksforgeeks.org/check-if-pair-with-given-sum-exists-in-array/',
                'starter_code_python': """class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        # Write your code here
        pass
""",
                'starter_code_cpp': """#include <vector>
#include <unordered_map>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        // Write your code here
        return {};
    }
};
""",
                'starter_code_java': """import java.util.HashMap;

class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Write your code here
        return new int[]{};
    }
}
""",
                'solution_python': """class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        seen = {}
        for index, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], index]
            seen[num] = index
        return []
""",
                'solution_cpp': """class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int, int> seen;
        for (int i = 0; i < nums.size(); i++) {
            int complement = target - nums[i];
            if (seen.find(complement) != seen.end()) {
                return {seen[complement], i};
            }
            seen[nums[i]] = i;
        }
        return {};
    }
};
""",
                'solution_java': """class Solution {
    public int[] twoSum(int[] nums, int target) {
        HashMap<Integer, Integer> seen = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (seen.containsKey(complement)) {
                return new int[]{seen.get(complement), i};
            }
            seen.put(nums[i], i);
        }
        return new int[]{};
    }
}
""",
                'editorial_explanation': """### Approach: One-Pass Hash Map
Instead of checking every pair with a nested loop ($O(N^2)$), we maintain a hash map where each key is a number from the array and the value is its corresponding index.
As we iterate through the array once:
1. Compute `complement = target - current_number`.
2. Check if `complement` is already stored in the hash map.
3. If yes, we immediately return `[seen[complement], current_index]`.
4. Otherwise, insert `current_number` with its index into the map.""",
                'time_complexity': 'O(N)',
                'space_complexity': 'O(N)',
                'is_daily_challenge': True,
                'acceptance_rate': 52.4,
                'points': 10
            }
        )

        q2, _ = CodingQuestion.objects.get_or_create(
            title='Valid Parentheses',
            defaults={
                'category': pcat_strings,
                'difficulty': 'Easy',
                'description': """Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket of the same type.""",
                'input_format': 's: str',
                'output_format': 'bool',
                'constraints': '1 <= s.length <= 10^4\ns consists of parentheses only ()[]{}.',
                'example_1_input': 's = "()[]{}"',
                'example_1_output': 'true',
                'example_2_input': 's = "(]"',
                'example_2_output': 'false',
                'hints': 'Use a LIFO Stack data structure. Whenever you encounter a closing bracket, check if it matches the top of the stack.',
                'leetcode_url': 'https://leetcode.com/problems/valid-parentheses/',
                'starter_code_python': """class Solution:
    def isValid(self, s: str) -> bool:
        # Write your code here
        pass
""",
                'starter_code_cpp': """#include <string>
#include <stack>
using namespace std;

class Solution {
public:
    bool isValid(string s) {
        // Write your code here
        return false;
    }
};
""",
                'starter_code_java': """import java.util.Stack;

class Solution {
    public boolean isValid(String s) {
        // Write your code here
        return false;
    }
}
""",
                'solution_python': """class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        mapping = {')': '(', '}': '{', ']': '['}
        for char in s:
            if char in mapping:
                top_element = stack.pop() if stack else '#'
                if mapping[char] != top_element:
                    return False
            else:
                stack.append(char)
        return not stack
""",
                'solution_cpp': """class Solution {
public:
    bool isValid(string s) {
        stack<char> st;
        for (char c : s) {
            if (c == '(' || c == '{' || c == '[') {
                st.push(c);
            } else {
                if (st.empty()) return false;
                char top = st.top();
                if ((c == ')' && top != '(') ||
                    (c == '}' && top != '{') ||
                    (c == ']' && top != '[')) {
                    return false;
                }
                st.pop();
            }
        }
        return st.empty();
    }
};
""",
                'solution_java': """class Solution {
    public boolean isValid(String s) {
        Stack<Character> stack = new Stack<>();
        for (char c : s.toCharArray()) {
            if (c == '(') stack.push(')');
            else if (c == '{') stack.push('}');
            else if (c == '[') stack.push(']');
            else if (stack.isEmpty() || stack.pop() != c) return false;
        }
        return stack.isEmpty();
    }
}
""",
                'editorial_explanation': """### Stack Intuition
A closing bracket must match the most recently opened bracket. This Last-In-First-Out (LIFO) order matches the stack data structure perfectly.""",
                'time_complexity': 'O(N)',
                'space_complexity': 'O(N)',
                'is_daily_challenge': False,
                'acceptance_rate': 41.2,
                'points': 10
            }
        )

        q3, _ = CodingQuestion.objects.get_or_create(
            title='Longest Substring Without Repeating Characters',
            defaults={
                'category': pcat_strings,
                'difficulty': 'Medium',
                'description': """Given a string `s`, find the length of the longest substring without repeating characters.""",
                'input_format': 's: str',
                'output_format': 'int',
                'constraints': '0 <= s.length <= 5 * 10^4\ns consists of English letters, digits, symbols and spaces.',
                'example_1_input': 's = "abcabcbb"',
                'example_1_output': '3',
                'example_1_explanation': 'The answer is "abc", with the length of 3.',
                'hints': 'Use a Sliding Window with two pointers [left, right] and a hash set or dictionary of last seen positions.',
                'leetcode_url': 'https://leetcode.com/problems/longest-substring-without-repeating-characters/',
                'starter_code_python': """class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        pass
""",
                'starter_code_cpp': """class Solution {
public:
    int lengthOfLongestSubstring(string s) {
        return 0;
    }
};
""",
                'starter_code_java': """class Solution {
    public int lengthOfLongestSubstring(String s) {
        return 0;
    }
}
""",
                'solution_python': """class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        char_map = {}
        left = 0
        max_len = 0
        for right, char in enumerate(s):
            if char in char_map and char_map[char] >= left:
                left = char_map[char] + 1
            char_map[char] = right
            max_len = max(max_len, right - left + 1)
        return max_len
""",
                'solution_cpp': """class Solution {
public:
    int lengthOfLongestSubstring(string s) {
        vector<int> lastIndex(256, -1);
        int left = 0, maxLen = 0;
        for (int right = 0; right < s.length(); right++) {
            if (lastIndex[s[right]] >= left) {
                left = lastIndex[s[right]] + 1;
            }
            lastIndex[s[right]] = right;
            maxLen = max(maxLen, right - left + 1);
        }
        return maxLen;
    }
};
""",
                'solution_java': """class Solution {
    public int lengthOfLongestSubstring(String s) {
        int[] lastIndex = new int[256];
        java.util.Arrays.fill(lastIndex, -1);
        int left = 0, maxLen = 0;
        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);
            if (lastIndex[c] >= left) {
                left = lastIndex[c] + 1;
            }
            lastIndex[c] = right;
            maxLen = Math.max(maxLen, right - left + 1);
        }
        return maxLen;
    }
}
""",
                'editorial_explanation': """### Sliding Window Technique
We maintain a window `[left, right]` where all characters are distinct. As `right` expands, if `s[right]` is already in the window, we jump `left` past the previous duplicate occurrence.""",
                'time_complexity': 'O(N)',
                'space_complexity': 'O(min(N, M))',
                'is_daily_challenge': True,
                'acceptance_rate': 34.8,
                'points': 20
            }
        )

        # Mark Two Sum as solved by student
        UserQuestionStatus.objects.get_or_create(
            user=student_user,
            question=q1,
            defaults={'status': 'solved', 'user_code': q1.solution_python, 'selected_language': 'python'}
        )

        # 8. Career Roadmaps
        rm_fs, _ = Roadmap.objects.get_or_create(
            title='Full-Stack Web Developer Roadmap',
            defaults={
                'target_role': 'Full-Stack Software Engineer',
                'icon': 'bi-globe2',
                'banner_color': 'linear-gradient(135deg, #0d6efd, #0dcaf0)',
                'short_description': 'Step-by-step master roadmap covering modern HTML/CSS, JavaScript/TypeScript, Python/Django, relational databases, REST APIs, and cloud deployment.',
                'description': """This comprehensive roadmap provides an actionable, sequenced learning journey designed to transform students into capable full-stack developers ready for software engineering internships and junior SDE roles.""",
                'estimated_time': '6-8 Months (Estimated)',
                'order': 1,
                'is_published': True
            }
        )

        stage1, _ = RoadmapStage.objects.get_or_create(
            roadmap=rm_fs,
            title='Stage 1: Frontend Foundations & Responsive Design',
            defaults={'level': 'Beginner', 'order': 1, 'estimated_stage_time': '4-6 Weeks (Estimated)', 'description': 'Master modern semantic HTML5, CSS3 layout models (Flexbox & CSS Grid), and responsive design principles.'}
        )
        RoadmapTopic.objects.get_or_create(
            stage=stage1,
            title='Semantic HTML5 & Accessibility (a11y)',
            defaults={'order': 1, 'description': 'Structure web documents properly using semantic tags, ARIA roles, and keyboard navigation standards.', 'prerequisites': 'None', 'project_ideas': 'Build a semantic academic resume and portfolio page.'}
        )
        RoadmapTopic.objects.get_or_create(
            stage=stage1,
            title='CSS Flexbox & CSS Grid Responsive Layouts',
            defaults={'order': 2, 'description': 'Build adaptable UI components and dashboard layouts that look flawless across desktop, tablet, and mobile screens.', 'prerequisites': 'HTML5 basics', 'project_ideas': 'Design a responsive e-commerce product card grid with media queries.'}
        )

        stage2, _ = RoadmapStage.objects.get_or_create(
            roadmap=rm_fs,
            title='Stage 2: Backend Development, Python & Relational Databases',
            defaults={'level': 'Intermediate', 'order': 2, 'estimated_stage_time': '6-8 Weeks (Estimated)', 'description': 'Build server-side logic, design normalized database schemas, and create robust RESTful endpoints with Django.'}
        )
        RoadmapTopic.objects.get_or_create(
            stage=stage2,
            title='Django MTV Architecture & Model Migrations',
            defaults={'order': 1, 'description': 'Understand Django Models, Templates, and Views. Design database schemas and perform zero-downtime migrations.', 'related_course': course_web, 'related_note': note2, 'project_ideas': 'Build a student book exchange portal with user authentication.'}
        )
        RoadmapTopic.objects.get_or_create(
            stage=stage2,
            title='Relational Databases, Normalization & SQL Optimization',
            defaults={'order': 2, 'description': 'Master PostgreSQL queries, indexes, joins, and normal forms (1NF to BCNF).', 'related_note': note2, 'project_ideas': 'Write complex analytical queries for student grade tracking.'}
        )

        stage3, _ = RoadmapStage.objects.get_or_create(
            roadmap=rm_fs,
            title='Stage 3: Advanced Systems, Security & Cloud Deployment',
            defaults={'level': 'Advanced', 'order': 3, 'estimated_stage_time': '6-8 Weeks (Estimated)', 'description': 'Authentication security, Docker containerization, CI/CD pipelines, and production deployment on Render and AWS.'}
        )
        RoadmapTopic.objects.get_or_create(
            stage=stage3,
            title='Production Deployment on Render with PostgreSQL',
            defaults={'order': 1, 'description': 'Configure WhiteNoise static file caching, Gunicorn WSGI workers, and environment variable secrets for production.', 'project_ideas': 'Deploy Student Success Hub live on Render with automated database backups.'}
        )

        # Enroll student in roadmap
        UserRoadmapEnrollment.objects.get_or_create(user=student_user, roadmap=rm_fs)

        # 9. Notifications
        Notification.objects.get_or_create(
            user=student_user,
            title='Welcome to Student Success Hub!',
            defaults={
                'message': 'Explore curated programming courses, download verified semester notes, and practice DSA problems.',
                'link_url': '/courses/',
                'notification_type': 'system'
            }
        )
        Notification.objects.get_or_create(
            user=student_user,
            title='Upcoming Live Class: Dynamic Programming',
            defaults={
                'message': 'Your live Google Meet class starts today at 6:30 PM. Click to view meeting room details.',
                'link_url': f'/live-classes/{class_live.pk}/',
                'notification_type': 'class'
            }
        )

        self.stdout.write(self.style.SUCCESS("Database successfully seeded with courses, notes, classes, coding challenges, and roadmaps!"))
