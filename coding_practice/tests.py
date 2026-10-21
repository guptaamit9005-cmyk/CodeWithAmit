from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import PracticeSet, ProblemCategory, CodingQuestion, UserQuestionStatus

class CodingPracticeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='admin', password='admin123', email='admin@test.com')
        self.student_user = User.objects.create_user(username='student', password='student123')
        
        self.pset = PracticeSet.objects.create(title='450 DSA Sheet')
        self.cat = ProblemCategory.objects.create(name='Arrays & Hashing')
        self.question = CodingQuestion.objects.create(
            title='Two Sum',
            practice_set=self.pset,
            category=self.cat,
            difficulty='Easy',
            platform='LeetCode',
            leetcode_url='https://leetcode.com/problems/two-sum/',
            company_tags='Google, Amazon',
            description='Given an array of integers, return indices of two numbers that add to target.',
            points=10,
        )

    def test_problem_list_displays_question_and_leetcode_url(self):
        response = self.client.get(reverse('coding_practice:problem_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Two Sum')
        self.assertContains(response, 'https://leetcode.com/problems/two-sum/')
        self.assertContains(response, 'Solve on LeetCode')

    def test_admin_can_add_leetcode_question(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('coding_practice:add_question'), {
            'title': 'Reverse Linked List',
            'category': self.cat.id,
            'difficulty': 'Easy',
            'platform': 'LeetCode',
            'leetcode_url': 'https://leetcode.com/problems/reverse-linked-list/',
            'company_tags': 'Amazon, Apple',
            'points': 10,
            'description': 'Reverse a singly linked list.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CodingQuestion.objects.filter(title='Reverse Linked List').exists())
        created_q = CodingQuestion.objects.get(title='Reverse Linked List')
        self.assertEqual(created_q.leetcode_url, 'https://leetcode.com/problems/reverse-linked-list/')

    def test_student_cannot_access_add_question(self):
        self.client.login(username='student', password='student123')
        response = self.client.get(reverse('coding_practice:add_question'))
        self.assertEqual(response.status_code, 302)

    def test_toggle_solved_status(self):
        self.client.login(username='student', password='student123')
        # Mark as solved
        response = self.client.get(reverse('coding_practice:toggle_solved', args=[self.question.slug]))
        self.assertEqual(response.status_code, 302)
        status = UserQuestionStatus.objects.get(user=self.student_user, question=self.question)
        self.assertEqual(status.status, 'solved')
        
        # Toggle back to unattempted
        self.client.get(reverse('coding_practice:toggle_solved', args=[self.question.slug]))
        status.refresh_from_db()
        self.assertEqual(status.status, 'unattempted')
