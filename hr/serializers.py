from rest_framework import serializers
from .models import Employee, Attendance


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'emp_id', 'full_name', 'email', 'department']

    def validate_emp_id(self, value):
        if not value.strip():
            raise serializers.ValidationError('Employee ID cannot be empty')
        return value


class AttendanceSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'date', 'status']

    def validate(self, data):
        # Ensure status is valid
        if data.get('status') not in dict(Attendance.STATUS_CHOICES).keys():
            raise serializers.ValidationError({'status': 'Invalid status'})
        return data
