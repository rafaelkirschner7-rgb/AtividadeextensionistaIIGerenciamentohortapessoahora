from django.conf import settings
from django.db import models
from django.utils import timezone


# Modelo que representa um Projeto
class Project(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Modelo que representa uma entrada de tempo (timesheet)
class TimeEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='entries')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='entries')
    date = models.DateField(default=timezone.localdate)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-start_time']

# Método que calcula a duração da entrada em horas
    def duration_hours(self):
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return round(delta.total_seconds() / 3600, 2)
        return 0.0

    def __str__(self):
        return f'{self.user} - {self.project} - {self.date}'



