from rest_framework import routers
from django.urls import path, include
from .views import *

app_name = "task"

router = routers.SimpleRouter()
urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='user-register'),
    path('api/', include(router.urls)),
    path('api/profiles/', My_page.as_view()),
    path('api/task_for_customer/', List_and_create_task_for_customer.as_view()),
    path('api/get_task/<int:pk>/', Get_Task.as_view()),
    path('api/apply_task/', Apply_task.as_view()),
    path('api/task_for_staff/', AvailableTaskForStaff.as_view()),
    path('api/my_task/', AllMyTaskStaff.as_view()),
    path('api/create_task/', StaffCreateTask.as_view()),
    path('api/edit_task/<int:pk>/', EditTask.as_view()),
    path('api/add_staff_in_task/<int:pk>/',AddStaffInTask.as_view()),
    path('api/show_staff/', AllStaff.as_view()),
    path('api/show_all_customer/',ShowCustomerForStaff.as_view()),
]
