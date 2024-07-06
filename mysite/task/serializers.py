from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Task, Profile
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework.authtoken.models import Token
from django.db import transaction

UserModel = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('phone', 'status', 'photo')


class UserCreateSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'profile')

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, **profile_data)
        Token.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'id']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

    def validate_customer(self, value):
        if value.status != 'Заказачик':
            raise serializers.ValidationError({'Error': 'Отказано в доступе'})
        return value

    def validate_staff(self, value):
        if value.status != 'Сотрудник':
            raise serializers.ValidationError({'Error': 'Отказано в доступе'})
        return value

    def validate_text(self, value):
        if not value:
            raise serializers.ValidationError({'text': 'Строчка не может быть пустой'})
        return value

    def validate_report(self, value):
        if not value:
            raise serializers.ValidationError({'text': 'Строчка не может быть пустой'})
        return value
