from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Profile, Task, GenderStatus, Readiness

class UserCreateAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword123',
            'email': 'test@example.com'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_create_user(self):
        response = self.client.post('/api/user/create/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)

class TaskModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        self.profile = Profile.objects.create(
            user=self.user,
            phone=123456789,
            status=GenderStatus.customer,
            photo='path/to/photo.jpg'
        )
        self.task = Task.objects.create(
            text='Test Task',
            owner=self.profile,
            customer=self.profile
        )

    def test_task_creation(self):
        self.assertEqual(self.task.text, 'Test Task')
        self.assertEqual(self.task.owner, self.profile)
        self.assertEqual(self.task.customer, self.profile)
        self.assertEqual(self.task.status, Readiness.waiting)



