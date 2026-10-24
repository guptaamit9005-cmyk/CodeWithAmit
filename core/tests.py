from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from courses.models import CourseCategory, Course, Lesson, Quiz, QuizQuestion, Enrollment
from notes.models import NoteCategory, Note
from live_classes.models import LiveClass, ClassAttendee
from coding_practice.models import ProblemCategory, CodingQuestion, UserQuestionStatus
from roadmaps.models import Roadmap, RoadmapStage, RoadmapTopic, UserRoadmapEnrollment
from datetime import date, time

class StudentSuccessHubTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='teststudent', password='testpassword123', email='test@hub.org')
        
        # Course setup
        self.cat = CourseCategory.objects.create(name='Algorithms')
        self.course = Course.objects.create(
            title='Intro to Algorithms',
            category=self.cat,
            instructor=self.user,
            short_description='Algorithmic foundations',
            description='Detailed syllabus',
            is_published=True
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            title='Lesson 1',
            order=1,
            is_free_preview=True,
            content='Lesson 1 content'
        )

        # Quiz setup
        self.quiz = Quiz.objects.create(lesson=self.lesson, title='Quiz 1', passing_score=70)
        self.qq = QuizQuestion.objects.create(
            quiz=self.quiz,
            question_text='What is 2+2?',
            option_a='3', option_b='4', option_c='5', option_d='6',
            correct_option='B'
        )

        # Note setup
        self.note_cat = NoteCategory.objects.create(name='Core CS')
        self.note = Note.objects.create(
            title='OS Handwritten Notes',
            category=self.note_cat,
            subject='Operating Systems',
            uploader=self.user,
            is_approved=True
        )

        # Live class setup
        self.live_class = LiveClass.objects.create(
            title='Live Graphs Session',
            description='BFS and DFS',
            instructor=self.user,
            scheduled_date=date.today(),
            start_time=time(18, 0),
            google_meet_url='https://meet.google.com/test-meet',
            status='upcoming'
        )

        # Question setup
        self.pcat = ProblemCategory.objects.create(name='Arrays')
        self.question = CodingQuestion.objects.create(
            title='Two Sum',
            category=self.pcat,
            difficulty='Easy',
            description='Find indices of two numbers',
            example_1_input='[2,7], target=9',
            example_1_output='[0,1]',
            starter_code_python='def twoSum(): pass',
            solution_python='def twoSum(): return [0,1]'
        )

        # Roadmap setup
        self.roadmap = Roadmap.objects.create(
            title='Full-Stack Path',
            target_role='Full Stack SDE',
            short_description='Path from 0 to 1',
            description='Detailed path'
        )
        self.stage = RoadmapStage.objects.create(roadmap=self.roadmap, title='Stage 1', order=1)
        self.topic = RoadmapTopic.objects.create(stage=self.stage, title='HTML5', order=1)

    def test_home_page(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CodeWithAmit')

    def test_global_search(self):
        response = self.client.get(reverse('core:search') + '?q=Algorithms')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Intro to Algorithms')

    def test_authentication_login_logout(self):
        # Login
        logged_in = self.client.login(username='teststudent', password='testpassword123')
        self.assertTrue(logged_in)
        # Dashboard
        resp = self.client.get(reverse('dashboard:student_dashboard'))
        self.assertEqual(resp.status_code, 200)
        # Logout
        resp_logout = self.client.get(reverse('accounts:logout'))
        self.assertEqual(resp_logout.status_code, 302)

    def test_course_flow_and_quiz(self):
        self.client.login(username='teststudent', password='testpassword123')
        # Detail view
        resp = self.client.get(reverse('courses:course_detail', args=[self.course.slug]))
        self.assertEqual(resp.status_code, 200)
        # Enroll
        resp_enroll = self.client.get(reverse('courses:enroll_course', args=[self.course.slug]))
        self.assertEqual(resp_enroll.status_code, 302)
        self.assertTrue(Enrollment.objects.filter(user=self.user, course=self.course).exists())
        # Submit Quiz
        quiz_data = {f'question_{self.qq.id}': 'B'}
        resp_quiz = self.client.post(
            reverse('courses:submit_quiz', args=[self.course.slug, self.lesson.slug]),
            data=quiz_data
        )
        self.assertEqual(resp_quiz.status_code, 200)
        self.assertContains(resp_quiz, 'Congratulations! You Passed!')

    def test_coding_practice_execution_and_submission(self):
        self.client.login(username='teststudent', password='testpassword123')
        # Problem detail
        resp = self.client.get(reverse('coding_practice:problem_detail', args=[self.question.slug]))
        self.assertEqual(resp.status_code, 200)
        # Run code API
        resp_run = self.client.post(
            reverse('coding_practice:run_code', args=[self.question.slug]),
            data='{"code": "def twoSum(): return [0,1]", "language": "python"}',
            content_type='application/json'
        )
        self.assertEqual(resp_run.status_code, 200)
        self.assertFalse(resp_run.json()['success'])
        # Submit code API
        resp_submit = self.client.post(
            reverse('coding_practice:submit_code', args=[self.question.slug]),
            data='{"code": "def twoSum(nums, target): return [0, 1]", "language": "python"}',
            content_type='application/json'
        )
        self.assertEqual(resp_submit.status_code, 200)
        self.assertFalse(resp_submit.json()['success'])
        # 1-click toggle solved (AJAX)
        resp_toggle = self.client.post(
            reverse('coding_practice:toggle_solved', args=[self.question.slug]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp_toggle.status_code, 200)
        self.assertTrue(resp_toggle.json()['success'])
        self.assertTrue(UserQuestionStatus.objects.filter(user=self.user, question=self.question, status='solved').exists())

    def test_live_class_registration_and_join(self):
        self.client.login(username='teststudent', password='testpassword123')
        # Register
        resp_reg = self.client.get(reverse('live_classes:register_class', args=[self.live_class.pk]))
        self.assertEqual(resp_reg.status_code, 302)
        self.assertTrue(ClassAttendee.objects.filter(user=self.user, live_class=self.live_class).exists())
        # Join (redirects to Google Meet)
        resp_join = self.client.get(reverse('live_classes:join_class', args=[self.live_class.pk]))
        self.assertEqual(resp_join.status_code, 302)
        self.assertEqual(resp_join.url, self.live_class.google_meet_url)

    def test_roadmap_topic_ajax_toggle(self):
        self.client.login(username='teststudent', password='testpassword123')
        # Toggle topic completion
        resp_toggle = self.client.post(
            reverse('roadmaps:toggle_topic_progress', args=[self.roadmap.slug, self.topic.id]),
            data='{"is_completed": true}',
            content_type='application/json'
        )
        self.assertEqual(resp_toggle.status_code, 200)
        self.assertTrue(resp_toggle.json()['is_completed'])
        self.assertEqual(resp_toggle.json()['completion_percent'], 100)
