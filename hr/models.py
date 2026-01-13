from django.db import models


class Employee(models.Model):
    emp_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.emp_id} - {self.full_name}"


class Attendance(models.Model):
    STATUS_PRESENT = 'Present'
    STATUS_ABSENT = 'Absent'
    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Present'),
        (STATUS_ABSENT, 'Absent'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.emp_id} | {self.date} | {self.status}"
