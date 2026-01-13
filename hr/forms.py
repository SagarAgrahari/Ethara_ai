from django import forms
from .models import Employee, Attendance


class CustomDateInput(forms.DateInput):
    input_type = 'text'
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control flatpickr-date',
            'placeholder': 'Select date (YYYY-MM-DD)',
            'data-dateFormat': 'Y-m-d'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['emp_id', 'full_name', 'email', 'department']
        widgets = {
            'emp_id': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_emp_id(self):
        emp_id = self.cleaned_data.get('emp_id')
        if emp_id:
            # Check if emp_id already exists (excluding current instance if editing)
            existing = Employee.objects.filter(emp_id=emp_id)
            if self.instance.pk:
                # If editing, exclude the current employee
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(
                    f"Employee ID '{emp_id}' is already assigned to another employee. "
                    "Please use a unique Employee ID.",
                    code='duplicate_emp_id'
                )
        return emp_id

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists (excluding current instance if editing)
            existing = Employee.objects.filter(email=email)
            if self.instance.pk:
                # If editing, exclude the current employee
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(
                    f"An employee with email '{email}' already exists. "
                    "Please use a unique email address.",
                    code='duplicate_email'
                )
        return email


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'status']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'date': CustomDateInput(),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
