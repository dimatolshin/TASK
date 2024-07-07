from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Profile, Task
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import json

class TaskTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.profile = Profile.objects.create(user=self.user, phone='1234567890', photo='path/to/photo.jpg',
                                              status='Заказчик')
        self.task = Task.objects.create(customer=self.profile, text='Test Task', owner=self.profile)

    def test_create_task(self):
        url = reverse('task:List_and_create_task_for_customer')
        data = {'text': 'New Test Task'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(Task.objects.get(id=2).text, 'New Test Task')

    def test_list_tasks(self):
        url = reverse('task:List_and_create_task_for_customer')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def tearDown(self):
        # Очищаем за собой
        self.user.delete()
        self.profile.delete()
        self.task.delete()
