from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import *


class UserUpgradeInline(admin.TabularInline):
    model = Profile
    extra = 1


admin.site.unregister(User)


@admin.register(Profile)
class UserUpgradeAdmin(admin.ModelAdmin):
    list_display = ('username', 'status', 'get_user_permissions_display',)
    list_filter = ('status',)
    search_fields = ('username', 'email', 'phone', 'get_user_permissions_display',)

    def get_user_permissions_display(self, obj):
        return ", ".join([p.codename for p in obj.user.user_permissions.all()])

    def username(self, obj):
        return obj.user.username

    get_user_permissions_display.short_description = 'Права пользователя'


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [UserUpgradeInline]


class TaskAdmin(admin.ModelAdmin):
    model = Task
    list_display = ('text', 'owner', 'customer', 'staff', 'status', 'data_start', 'data_update',
                    'data_finish')
    list_filter = ('status', 'owner', 'customer', 'staff', 'data_start', 'data_finish')
    search_fields = ('text', 'owner__username', 'customer__username', 'staff__username')
    ordering = ('-data_start',)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return [
                (None, {'fields': ('text', 'owner', 'customer', 'staff', 'status',)}),
            ]
        return [
            (None, {'fields': ('text', 'owner', 'customer', 'staff', 'status')}),
            ('Даты', {'fields': ('data_update', 'data_finish')}),
            ('Отчет', {'fields': ('report',)}),
        ]


admin.site.register(Task, TaskAdmin)
