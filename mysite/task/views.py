from datetime import date

from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status, mixins
from djoser.serializers import UserCreateSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .models import *
from .serializers import *


class UserCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get(user=user)
            data = serializer.data
            data['token'] = token.key
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class My_page(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        data = self.request.user.profile
        return Response(ProfileSerializer(data).data)


class List_and_create_task_for_customer(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if self.request.user.profile.status == 'Заказчик':
            customer = self.request.user.profile
            task = Task.objects.create(customer=customer, text=request.data['text'], owner=customer)
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
        else:
            return Response({'Error': 'Отказано в доступе'}, status=status.HTTP_403_FORBIDDEN)

    def list(self, request):
        if self.request.user.profile.status == 'Заказчик':
            queryset = Task.objects.filter(customer=self.request.user.profile)
            serializer = TaskSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Отказано в доступе'}, status=status.HTTP_403_FORBIDDEN)


class Apply_task(APIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if self.request.user.profile.status == 'Сотрудник':
            task = Task.objects.get(pk=self.request.data['task_pk'])
            task.staff = self.request.user.profile
            task.status = Readiness.in_progress
            task.data_update = date.today()
            task.save()
            return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Отказано в доступе'}, status=status.HTTP_403_FORBIDDEN)


class Get_Task(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        task = Task.objects.get(pk=pk)
        if self.request.user.profile == task.staff:
            return Response(TaskSerializer(task).data)
        if self.request.user.has_perm('task.access_all_tasks'):
            return Response(TaskSerializer(task).data)
        if self.request.user.profile == task.customer:
            return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Отказано в доступе'}, status=status.HTTP_403_FORBIDDEN)


class AvailableTaskForStaff(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.status == 'Сотрудник':
            return Task.objects.filter(staff=None)
        if user.has_perm('task.access_all_tasks'):
            return Task.objects.all()
        return Task.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = TaskSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Отказано в доступе'}, status=status.HTTP_403_FORBIDDEN)


class AllMyTaskStaff(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.status == 'Сотрудник':
            return Task.objects.filter(staff=user.profile)
        return Task.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = TaskSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Отказано в доступе'}, status=status.HTTP_403_FORBIDDEN)


class StaffCreateTask(generics.CreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if self.request.user.has_perm('task.can_create'):
            customer = Profile.objects.get(pk=self.request.data['profile_pk'])
            task = Task.objects.create(owner=self.request.user.profile, customer=customer,
                                       text=self.request.data['text'])
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
        else:
            return Response({'Error': 'Отказано в доступе'}, status=status.HTTP_403_FORBIDDEN)


class EditTask(generics.UpdateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, pk):
        task = Task.objects.get(pk=pk)
        if task.staff == self.request.user.profile and task.status != Readiness.completed:
            task.report = self.request.data['report']
            task.status = Readiness.completed
            task.data_finish = date.today()
            task.save()
            return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Задание выполнено'}, status=status.HTTP_403_FORBIDDEN)


class AddStaffInTask(generics.UpdateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, pk):
        task = Task.objects.get(pk=pk)
        if task.staff == None and self.request.user.has_perm('task.can_add_staff'):
            staff = Profile.objects.get(pk=self.request.data['profile_pk'])
            task.staff = staff
            task.status = Readiness.in_progress
            task.data_update = date.today()
            task.save()
            return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Отказано в доступе'}, status=status.HTTP_403_FORBIDDEN)


class AllStaff(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm(
                'task.access_all_staff') or self.request.user.profile.status == GenderStatus.staff:
            return Profile.objects.filter(status=GenderStatus.staff)
        return Profile.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = ProfileSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Отказано в доступе'}, status=status.HTTP_403_FORBIDDEN)


class ShowCustomerForStaff(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.profile.status == GenderStatus.staff:
            return Profile.objects.filter(status=GenderStatus.customer)
        return Profile.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = ProfileSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Отказано в доступе'}, status=status.HTTP_403_FORBIDDEN)
