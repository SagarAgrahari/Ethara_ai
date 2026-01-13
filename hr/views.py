from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from calendar import monthcalendar

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Employee, Attendance
from .serializers import EmployeeSerializer, AttendanceSerializer
from .forms import EmployeeForm, AttendanceForm


def get_working_days_count(year, month):
    """Calculate working days (Monday-Friday) for a given month"""
    working_days = 0
    for week in monthcalendar(year, month):
        for day_index, day in enumerate(week):
            if day == 0:  # Skip days from other months
                continue
            if day_index < 5:  # Monday=0 to Friday=4
                working_days += 1
    return working_days


def dashboard(request):
    total_employees = Employee.objects.count()
    total_attendance = Attendance.objects.count()
    present_counts = (
        Attendance.objects.filter(status=Attendance.STATUS_PRESENT)
        .values('employee')
        .annotate(present_days=Count('id'))
    )
    present_map = {p['employee']: p['present_days'] for p in present_counts}
    employees = list(Employee.objects.all())
    for e in employees:
        e.present_days = present_map.get(e.id, 0)
    return render(request, 'dashboard_enterprise.html', {
        'total_employees': total_employees,
        'total_attendance': total_attendance,
        'employees': employees,
    })


def employees_list(request):
    employees = Employee.objects.all().order_by('emp_id')
    return render(request, 'employees_list_enterprise.html', {'employees': employees})


def employee_add(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee added successfully')
            return redirect(reverse('employees_list'))
    else:
        form = EmployeeForm()
    return render(request, 'employee_add_enterprise.html', {'form': form})


def employee_delete(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    emp.delete()
    messages.success(request, 'Employee deleted')
    return redirect(reverse('employees_list'))


def attendance_mark(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Attendance marked successfully')
            except Exception as e:
                messages.error(request, f'Error: {e}')
            return redirect(reverse('attendance_mark'))
    else:
        form = AttendanceForm()
    return render(request, 'attendance_mark_enterprise.html', {'form': form})


def attendance_list(request, employee_id=None):
    qs = Attendance.objects.select_related('employee').order_by('-date')
    
    selected_employee = None
    selected_date = None
    current_date = datetime.now()
    
    # Get filter parameters from request
    employee_param = request.GET.get('employee', '').strip()
    date_param = request.GET.get('date', '').strip()
    
    # Apply employee filter
    if employee_param:
        try:
            emp_id = int(employee_param)
            qs = qs.filter(employee_id=emp_id)
            selected_employee = int(emp_id)
        except (ValueError, TypeError):
            pass
    # Apply date filter
    if date_param:
        try:
            parsed = parse_date(date_param)
            if parsed:
                qs = qs.filter(date=parsed)
                selected_date = date_param
        except Exception:
            pass
    
    # Only use URL employee_id if no filters are applied
    if not employee_param and not date_param and employee_id:
        qs = qs.filter(employee_id=employee_id)
        selected_employee = int(employee_id)
    
    # Get all employees for the filter dropdown
    employees = Employee.objects.all().order_by('emp_id')
    
    # Calculate statistics
    attendance_stats = {}
    if selected_employee:
        # If employee is selected, show stats for current month
        try:
            employee_obj = Employee.objects.get(id=selected_employee)
            current_month = current_date.month
            current_year = current_date.year
            
            # Get working days for the month
            working_days = get_working_days_count(current_year, current_month)
            
            # Get attendance counts for this employee in current month
            attendance_records = Attendance.objects.filter(
                employee_id=selected_employee,
                date__year=current_year,
                date__month=current_month
            )
            
            present_count = attendance_records.filter(status=Attendance.STATUS_PRESENT).count()
            absent_count = attendance_records.filter(status=Attendance.STATUS_ABSENT).count()
            
            attendance_stats = {
                'employee_name': employee_obj.full_name,
                'employee_id': employee_obj.emp_id,
                'working_days': working_days,
                'present_days': present_count,
                'absent_days': absent_count,
                'pending_days': working_days - present_count - absent_count,
            }
        except (ValueError, Employee.DoesNotExist):
            pass
    
    context = {
        'attendances': qs,
        'employees': employees,
        'selected_employee': selected_employee,
        'selected_date': selected_date,
        'attendance_stats': attendance_stats,
    }
    
    return render(request, 'attendance_list_enterprise.html', context)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def create(self, request, *args, **kwargs):
        # handle unique constraint gracefully
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
