from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('employees/', views.employees_list, name='employees_list'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/delete/<int:pk>/', views.employee_delete, name='employee_delete'),
    path('attendance/mark/', views.attendance_mark, name='attendance_mark'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/employee/<int:employee_id>/', views.attendance_list, name='attendance_list_for_employee'),
]
