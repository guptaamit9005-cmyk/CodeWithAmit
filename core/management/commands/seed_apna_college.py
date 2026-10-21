import os
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
from tutorials.models import TutorialCategory, TutorialTopic

class Command(BaseCommand):
    help = 'Seeds Apna College batches, curated DSA sheet, notes, and lessons'

    def handle(self, *args, **options):
        self.stdout.write("Seeding Apna College flagship batches, DSA sheet, and resources...")

        # 1. Admin & Instructor Users
        admin_user, _ = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@codestyle.in',
            'first_name': 'Aman',
            'last_name': 'Dhattarwal',
            'is_staff': True,
            'is_superuser': True,
        })
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        admin_profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        admin_profile.role = 'admin'
        admin_profile.headline = 'Founder & Lead Educator | Apna College Platform'
        admin_profile.points = 2500
        admin_profile.streak_count = 35
        admin_profile.save()

        instructor_user, _ = User.objects.get_or_create(username='instructor', defaults={
            'email': 'shraddha@codestyle.in',
            'first_name': 'Shraddha',
            'last_name': 'Khapra',
            'is_staff': True,
        })
        instructor_user.set_password('instructor123')
        instructor_user.is_staff = True
        instructor_user.save()

        inst_profile, _ = UserProfile.objects.get_or_create(user=instructor_user)
        inst_profile.role = 'instructor'
        inst_profile.headline = 'Ex-Microsoft | Lead DSA & Web Dev Mentor'
        inst_profile.save()

        # 2. Categories
        cat_web, _ = CourseCategory.objects.get_or_create(
            name='Full-Stack Web Development',
            defaults={'icon': 'bi-globe', 'description': 'MERN stack, Next.js, Redux, PostgreSQL, MongoDB, and production cloud deployment.'}
        )
        cat_dsa, _ = CourseCategory.objects.get_or_create(
            name='Data Structures and Algorithms',
            defaults={'icon': 'bi-diagram-3', 'description': 'From basic loops to advanced dynamic programming, trees, and graphs.'}
        )
        cat_cpp, _ = CourseCategory.objects.get_or_create(
            name='C and C++ Systems',
            defaults={'icon': 'bi-cpu', 'description': 'Deep memory mastery, pointers, STL, and performance engineering.'}
        )
        cat_ai, _ = CourseCategory.objects.get_or_create(
            name='Machine Learning & Data Science',
            defaults={'icon': 'bi-robot', 'description': 'Python, NumPy, Pandas, Scikit-learn, Neural Networks, and Generative AI.'}
        )

        # 3. Flagship Batches (Apna College Style)
        # Batch 1: Delta 5.0
        delta_course, _ = Course.objects.update_or_create(
            title='Delta 5.0: Complete Full-Stack Web Development',
            defaults={
                'batch_name': 'Delta 5.0',
                'category': cat_web,
                'instructor': instructor_user,
                'difficulty': 'Beginner',
                'tag': 'Bestseller 🔥',
                'price': 4499,
                'original_price': 8999,
                'batch_start_date': '25th Oct | New Live Cohort',
                'language': 'Hinglish (Hindi + English)',
                'prerequisites': 'No Prior Coding Experience Required (Begins from Absolute Zero)',
                'estimated_hours': 120,
                'thumbnail_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=800&q=80',
                'short_description': 'India\'s #1 Full Stack Web Development course: HTML, CSS, JavaScript, React 19, Node.js, Express, MongoDB, Next.js, and 10+ Production Projects.',
                'description': """Delta 5.0 is the most comprehensive, student-trusted Full Stack Web Development program in India.
                
### What You Will Master:
- **Phase 1: Frontend Foundations** (HTML5 Semantic Markup, Modern CSS3 Flexbox/Grid, Responsive Mobile-First Design, TailwindCSS)
- **Phase 2: Modern JavaScript (ES6+)** (Closures, Promises, Async/Await, DOM Manipulation, Fetch API, Event Loop)
- **Phase 3: React 19 & Next.js** (Hooks, Custom Hooks, Redux Toolkit, Context API, Server Components, SSR)
- **Phase 4: Backend Engineering** (Node.js runtime, Express.js REST APIs, Authentication with JWT & OAuth, Middleware)
- **Phase 5: Databases & Architecture** (MongoDB Mongoose, PostgreSQL SQL modeling, Indexing, Cloud Atlas)
- **Phase 6: 10+ Real-World Production Projects** (Airbnb Clone with Stripe checkout, Real-Time Chat App with Socket.io, Social Media Platform, Code Reviewer AI)
- **Phase 7: Cloud & DevOps** (Docker containers, CI/CD GitHub Actions, Deployment on AWS/Vercel/Render)
- **Placement Perks**: 1:1 Live Doubt Clearing, Dedicated TA Support, Resume Review & Mock Interviews.""",
                'is_published': True,
                'is_featured': True,
            }
        )

        # Batch 2: Sigma 4.0
        sigma_course, _ = Course.objects.update_or_create(
            title='Sigma 4.0: Complete Placement Prep (DSA + Web Dev)',
            defaults={
                'batch_name': 'Sigma 4.0',
                'category': cat_dsa,
                'instructor': admin_user,
                'difficulty': 'Intermediate',
                'tag': 'Trending ⚡',
                'price': 5999,
                'original_price': 11999,
                'batch_start_date': 'Admissions Open | Placement Special',
                'language': 'Hinglish (Hindi + English)',
                'prerequisites': 'Zero to Hero — No prior college coding needed',
                'estimated_hours': 160,
                'thumbnail_url': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80',
                'short_description': 'The all-in-one placement prep program: 400+ Handpicked DSA questions in Java/C++, Complete Web Development, and Core CS Fundamentals (OS, DBMS, CN).',
                'description': """Sigma 4.0 is engineered specifically to help students crack campus placements and off-campus FAANG / Top Tech MNC job offers.

### What is Included in Sigma 4.0:
- **Part 1: 400+ Curated DSA Questions** in Java & C++ covering Arrays, Strings, Bit Manipulation, Linked Lists, Stacks, Queues, Binary Trees, Binary Search Trees, Heaps, Graphs, Dynamic Programming, and Greedy Algorithms.
- **Part 2: Full-Stack Web Development** from basics to full deployment so your resume has stand-out industry projects.
- **Part 3: Core CS Interview Subjects** (Database Management Systems, Operating Systems, Computer Networks, and Object-Oriented Programming).
- **Part 4: System Design** (High-Level Design & Low-Level Design fundamentals for SDE-1 interviews).
- **Part 5: 1:1 Live Doubt Assistance** with teaching assistants from top MNCs.""",
                'is_published': True,
                'is_featured': True,
            }
        )

        # Batch 3: Alpha Java DSA Masterclass
        alpha_course, _ = Course.objects.update_or_create(
            title='Alpha: Complete Java + DSA Masterclass',
            defaults={
                'batch_name': 'Alpha Batch',
                'category': cat_dsa,
                'instructor': instructor_user,
                'difficulty': 'Beginner',
                'tag': 'Highest Rated ⭐',
                'price': 3999,
                'original_price': 7999,
                'batch_start_date': 'Self-Paced with Live Doubt Sessions',
                'language': 'Hinglish (Hindi + English)',
                'prerequisites': 'No prerequisites required',
                'estimated_hours': 90,
                'thumbnail_url': 'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=800&q=80',
                'short_description': 'Master Java programming from basic syntax to advanced Object Oriented Design and solve 350+ LeetCode problems with optimal complexity.',
                'description': """Alpha is the premier Java & DSA program crafted by Shraddha Khapra (Ex-Microsoft).
                
Everything you need to master Java and solve medium to hard coding interview problems on LeetCode with confidence.""",
                'is_published': True,
                'is_featured': True,
            }
        )

        # Batch 4: C++ DSA Foundation
        cpp_course, _ = Course.objects.update_or_create(
            title='C++ DSA Foundation & Competitive Programming Bootcamp',
            defaults={
                'batch_name': 'C++ Bootcamp',
                'category': cat_cpp,
                'instructor': instructor_user,
                'difficulty': 'Intermediate',
                'tag': 'Popular 🚀',
                'price': 3499,
                'original_price': 6999,
                'batch_start_date': 'Instant Access',
                'language': 'Hinglish (Hindi + English)',
                'prerequisites': 'Interest in high-speed algorithms & competitive programming',
                'estimated_hours': 80,
                'thumbnail_url': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80',
                'short_description': 'Master C++ pointers, dynamic memory allocation, STL containers, time complexity analysis, and competitive programming patterns.',
                'description': """Master C++ from scratch, dive deep into memory layout, heap vs stack, pointer arithmetic, and learn to write blisteringly fast algorithms with C++ STL.""",
                'is_published': True,
                'is_featured': True,
            }
        )

        # 4. Add Lessons to Delta 5.0
        delta_lessons = [
            (1, 'HTML5 Foundations & Semantic Structure', 25, 'https://www.youtube.com/watch?v=HcOc7P5BMi4',
             'Learn semantic HTML5 tags (header, nav, main, article, section, footer), forms, accessibility attributes, and SEO best practices.',
             '<!DOCTYPE html>\n<html lang="en">\n<head><title>Delta Web</title></head>\n<body>\n  <header><h1>Welcome to Delta 5.0</h1></header>\n</body>\n</html>', 'html', True),
            (2, 'CSS3 Modern Layouts: Flexbox & Grid Masterclass', 35, 'https://www.youtube.com/watch?v=1PnVor36_40',
             'Complete mastery of CSS Flexbox (justify-content, align-items, flex-wrap) and CSS Grid (grid-template-columns, fr units, minmax, auto-fit).',
             '.container {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));\n  gap: 1.5rem;\n}', 'css', True),
            (3, 'JavaScript ES6+ Deep Dive: Closures, Promises & Async/Await', 45, 'https://www.youtube.com/watch?v=ajdRvxDWH4w',
             'Understanding the JavaScript Event Loop, call stack, microtask queue, closures, prototypal inheritance, and handling asynchronous HTTP requests with async/await.',
             'async function fetchUserData(userId) {\n  try {\n    const res = await fetch(`/api/users/${userId}`);\n    const data = await res.json();\n    return data;\n  } catch (err) {\n    console.error("Fetch failed:", err);\n  }\n}', 'javascript', True),
            (4, 'React 19 Core: Components, Props, and State Hooks', 40, 'https://www.youtube.com/watch?v=bMknfKXIFA8',
             'Introduction to React: Functional components, JSX syntax rules, useState and useEffect hooks, and unidirectional data flow.',
             'import { useState } from "react";\n\nexport default function Counter() {\n  const [count, setCount] = useState(0);\n  return <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>;\n}', 'javascript', False),
            (5, 'Backend REST APIs with Node.js & Express.js', 50, 'https://www.youtube.com/watch?v=7H_QH9nipNs',
             'Building robust RESTful APIs with Express: Routing, request/response cycle, middleware architecture, validation, and error handling.',
             'const express = require("express");\nconst app = express();\napp.use(express.json());\n\napp.get("/api/health", (req, res) => res.json({ status: "ok" }));\napp.listen(5000);', 'javascript', False),
            (6, 'Database Design with MongoDB & Mongoose ORM', 45, 'https://www.youtube.com/watch?v=ofme2o29ngU',
             'Designing document schemas with Mongoose, embedding vs referencing, indexing for fast lookups, and aggregation pipelines.',
             'const mongoose = require("mongoose");\nconst UserSchema = new mongoose.Schema({\n  name: { type: String, required: true },\n  email: { type: String, unique: true },\n  role: { type: String, default: "student" }\n});', 'javascript', False),
        ]

        for order, title, duration, video_url, content, code, lang, is_free in delta_lessons:
            lesson, _ = Lesson.objects.update_or_create(
                course=delta_course,
                order=order,
                defaults={
                    'title': title,
                    'duration_minutes': duration,
                    'video_url': video_url,
                    'content': content,
                    'code_snippet': code,
                    'code_language': lang,
                    'is_free_preview': is_free,
                }
            )

        # 5. Add Curated LeetCode DSA Problems (Apna College DSA Sheet)
        prob_cat_array, _ = ProblemCategory.objects.get_or_create(name='Arrays & Hashing', defaults={'icon': 'bi-grid-3x3'})
        prob_cat_two_pt, _ = ProblemCategory.objects.get_or_create(name='Two Pointers', defaults={'icon': 'bi-arrow-left-right'})
        prob_cat_tree, _ = ProblemCategory.objects.get_or_create(name='Trees & BST', defaults={'icon': 'bi-diagram-3'})
        prob_cat_dp, _ = ProblemCategory.objects.get_or_create(name='Dynamic Programming', defaults={'icon': 'bi-boxes'})
        prob_cat_graph, _ = ProblemCategory.objects.get_or_create(name='Graphs', defaults={'icon': 'bi-share'})
        prob_cat_ll, _ = ProblemCategory.objects.get_or_create(name='Linked List', defaults={'icon': 'bi-link-45deg'})

        curated_questions = [
            ('Two Sum', prob_cat_array, 'Easy', 'LeetCode', 'https://leetcode.com/problems/two-sum/',
             'Amazon, Google, Apple, Microsoft, Meta',
             'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.',
             'O(n)', 'O(n)', 10),

            ('Best Time to Buy and Sell Stock', prob_cat_array, 'Easy', 'LeetCode', 'https://leetcode.com/problems/best-time-to-buy-and-sell-stock/',
             'Amazon, Microsoft, Google, Uber',
             'You are given an array prices where prices[i] is the price of a given stock on the ith day. Return the maximum profit you can achieve from this transaction.',
             'O(n)', 'O(1)', 10),

            ('3Sum', prob_cat_two_pt, 'Medium', 'LeetCode', 'https://leetcode.com/problems/3sum/',
             'Google, Amazon, Meta, Microsoft, Apple',
             'Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.',
             'O(n^2)', 'O(1)', 20),

            ('Trapping Rain Water', prob_cat_two_pt, 'Hard', 'LeetCode', 'https://leetcode.com/problems/trapping-rain-water/',
             'Google, Amazon, Microsoft, Goldman Sachs',
             'Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.',
             'O(n)', 'O(1)', 30),

            ('Valid Parentheses', prob_cat_array, 'Easy', 'LeetCode', 'https://leetcode.com/problems/valid-parentheses/',
             'Amazon, Microsoft, Bloomberg, Meta',
             'Given a string s containing just the characters \'(\', \')\', \'{\', \'}\', \'[\' and \']\', determine if the input string is valid.',
             'O(n)', 'O(n)', 10),

            ('Reverse Linked List', prob_cat_ll, 'Easy', 'LeetCode', 'https://leetcode.com/problems/reverse-linked-list/',
             'Amazon, Apple, Microsoft, Google',
             'Given the head of a singly linked list, reverse the list, and return the reversed list.',
             'O(n)', 'O(1)', 10),

            ('Invert Binary Tree', prob_cat_tree, 'Easy', 'LeetCode', 'https://leetcode.com/problems/invert-binary-tree/',
             'Google, Amazon, Microsoft',
             'Given the root of a binary tree, invert the tree, and return its root.',
             'O(n)', 'O(h)', 10),

            ('Lowest Common Ancestor of a Binary Tree', prob_cat_tree, 'Medium', 'LeetCode', 'https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/',
             'Amazon, Meta, Microsoft, Google',
             'Given a binary tree, find the lowest common ancestor (LCA) of two given nodes in the tree.',
             'O(n)', 'O(h)', 20),

            ('Number of Islands', prob_cat_graph, 'Medium', 'LeetCode', 'https://leetcode.com/problems/number-of-islands/',
             'Amazon, Microsoft, Google, Bloomberg',
             'Given an m x n 2D binary grid grid which represents a map of \'1\'s (land) and \'0\'s (water), return the number of islands.',
             'O(m*n)', 'O(m*n)', 20),

            ('Coin Change', prob_cat_dp, 'Medium', 'LeetCode', 'https://leetcode.com/problems/coin-change/',
             'Amazon, Microsoft, Google, Apple',
             'You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money. Return the fewest number of coins needed.',
             'O(amount * n)', 'O(amount)', 20),

            ('Longest Increasing Subsequence', prob_cat_dp, 'Medium', 'LeetCode', 'https://leetcode.com/problems/longest-increasing-subsequence/',
             'Google, Amazon, Microsoft',
             'Given an integer array nums, return the length of the longest strictly increasing subsequence.',
             'O(n log n)', 'O(n)', 20),
        ]

        for title, cat, diff, plat, url, tags, desc, tc, sc, pts in curated_questions:
            CodingQuestion.objects.update_or_create(
                title=title,
                defaults={
                    'category': cat,
                    'difficulty': diff,
                    'platform': plat,
                    'leetcode_url': url,
                    'company_tags': tags,
                    'description': desc,
                    'time_complexity': tc,
                    'space_complexity': sc,
                    'points': pts,
                }
            )

        # 6. Hand-written Study Notes (Apna College Style)
        note_cat_cs, _ = NoteCategory.objects.get_or_create(name='Core CS Fundamentals', defaults={'icon': 'bi-cpu'})
        note_cat_lang, _ = NoteCategory.objects.get_or_create(name='Programming Cheatsheets', defaults={'icon': 'bi-code-square'})

        notes_data = [
            ('Operating Systems: Complete Process Scheduling, Deadlocks & Virtual Memory Notes',
             'Operating Systems', '4th Semester', 'C / C++', note_cat_cs,
             'Complete hand-written lecture notes covering CPU Scheduling (FCFS, SJF, Round Robin), Process Synchronization (Mutex, Semaphores), Deadlock detection & avoidance (Banker\'s Algorithm), and Virtual Memory Paging with diagrams.'),

            ('Database Management Systems: SQL, Normalization (1NF to BCNF) & Indexing Cheat Sheet',
             'DBMS', '3rd Semester', 'SQL', note_cat_cs,
             'Comprehensive university exam and placement revision notes: ACID properties, Relational Algebra, ER Modeling, Normalization from 1NF to BCNF with solved examples, B-Trees, and Query Optimization.'),

            ('Computer Networks: OSI 7-Layer Model, TCP/IP, Subnetting & Routing Protocols',
             'Computer Networks', '5th Semester', 'Networking', note_cat_cs,
             'Complete exam & interview guide: OSI vs TCP/IP model, IP addressing & CIDR subnetting formulas, Three-Way Handshake, DNS resolution, HTTP/HTTPS, and Congestion Control.'),

            ('Object-Oriented Programming (OOPS) in C++ & Java: 4 Pillars & Design Patterns',
             'OOPS', '2nd Semester', 'C++ / Java', note_cat_lang,
             'Crystal-clear explanations of Encapsulation, Abstraction, Inheritance, Polymorphism (Virtual functions, vtable), and common interview Design Patterns (Singleton, Factory, Observer).'),
        ]

        for n_title, subj, sem, lang, cat, desc in notes_data:
            Note.objects.update_or_create(
                title=n_title,
                defaults={
                    'subject': subj,
                    'semester': sem,
                    'programming_language': lang,
                    'category': cat,
                    'description': desc,
                    'uploader': admin_user,
                    'is_approved': True,
                    'download_count': 1420,
                }
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded Apna College flagship batches, curated DSA sheet, and university notes!"))
