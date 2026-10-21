from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import TutorialCategory, TutorialTopic

class TutorialTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='testadmin', password='password123', email='admin@test.com')
        self.regular_user = User.objects.create_user(username='teststudent', password='password123')
        
        self.category = TutorialCategory.objects.create(
            name='Python Tutorial',
            icon='bi-filetype-py',
            description='Learn Python from scratch'
        )
        self.topic1 = TutorialTopic.objects.create(
            category=self.category,
            chapter='Basics',
            title='Variables in Python',
            order=1,
            summary='Variables store data values in memory.',
            content='<p>In Python, variables are created when you assign a value to it.</p>',
            code_snippet='x = 5\nprint(x)',
            is_published=True
        )
        self.topic2 = TutorialTopic.objects.create(
            category=self.category,
            chapter='Basics',
            title='Data Types in Python',
            order=2,
            summary='Built-in data types in Python.',
            content='<p>Python has numeric, string, sequence, and mapping types.</p>',
            is_published=True
        )

    def test_tutorial_list_view(self):
        response = self.client.get(reverse('tutorials:tutorial_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Tutorial')

    def test_tutorial_detail_view(self):
        response = self.client.get(reverse('tutorials:tutorial_detail', args=[self.category.slug, self.topic1.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Variables in Python')
        self.assertContains(response, 'Data Types in Python')

    def test_next_and_previous_topics(self):
        self.assertEqual(self.topic1.get_next_topic(), self.topic2)
        self.assertIsNone(self.topic1.get_previous_topic())
        self.assertEqual(self.topic2.get_previous_topic(), self.topic1)

    def test_admin_can_add_topic(self):
        self.client.login(username='testadmin', password='password123')
        response = self.client.post(reverse('tutorials:add_topic'), {
            'category': self.category.id,
            'chapter': 'Control Flow',
            'title': 'If Else Statements',
            'order': 3,
            'summary': 'Conditional branching in Python',
            'content': '<p>If statements are used for condition checking.</p>',
            'code_snippet': 'if True: print("yes")',
            'code_language': 'python',
            'read_time': '3 min read',
            'is_published': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TutorialTopic.objects.filter(title='If Else Statements').exists())

    def test_regular_user_cannot_add_topic(self):
        self.client.login(username='teststudent', password='password123')
        response = self.client.get(reverse('tutorials:add_topic'))
        self.assertEqual(response.status_code, 302)
