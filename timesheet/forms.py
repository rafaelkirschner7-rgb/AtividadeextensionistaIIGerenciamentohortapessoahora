from django import forms
from .models import Project, TimeEntry

# Formulário baseado no modelo Project
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'active']


# Formulário baseado no modelo TimeEntry
class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['project', 'date', 'start_time', 'end_time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
