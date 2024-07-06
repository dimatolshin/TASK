from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class GenderStatus(models.TextChoices):
    customer = 'Заказчик',
    staff = 'Сотрудник',


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.IntegerField(unique=True)
    status = models.CharField(max_length=15, choices=GenderStatus.choices)
    photo = models.ImageField(upload_to='media')
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('группы'),
        blank=True,
        help_text=_(
            'Группы, к которым принадлежит этот пользователь. Пользователь получит все разрешения, предоставленные каждой из его групп.'),
        related_name="customuser_groups",  # Уникальное имя для обратной связи
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('права пользователя'),
        blank=True,
        help_text=_('специфические права для этого пользователя.'),
        related_name="customuser_user_permissions",  # Уникальное имя для обратной связи
        related_query_name="customuser",
    )

    class Meta:
        permissions = (
            ("can_create", "Может создавать задачи"),
            ("access_all_tasks", "Доступ ко всем задачам"),
            ("can_add_customer", "Может добавлять заказчика"),
            ("can_add_staff", "Может добавлять сотрудника"),
            ("access_all_staff", "Доступ ко всем сотрудникам"),
        )

    def __str__(self):
        return f'{self.user.username}'


class Readiness(models.TextChoices):
    waiting = 'Ожидание исолнителя',
    in_progress = 'В процессе',
    completed = 'Выполнено',


class Task(models.Model):
    text = models.TextField(max_length=300)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='task_owner')
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='task_customer')
    staff = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='task_staff', null=True, blank=True)
    status = models.CharField(max_length=30, choices=Readiness.choices, default=Readiness.waiting)
    data_start = models.DateField(auto_now_add=True)
    data_update = models.DateField(null=True, blank=True)
    data_finish = models.DateField(null=True, blank=True)
    report = models.TextField(max_length=300, )
