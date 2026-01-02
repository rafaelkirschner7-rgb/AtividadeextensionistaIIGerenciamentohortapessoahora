from django.utils import timezone
from .models import TimeEntry, Project

# Função para iniciar uma entrada de tempo (TimeEntry)
# Cria uma nova entrada de tempo vinculada ao usuário e ao projeto
# Define a data atual e a hora de início como o momento atual
def start_entry(user, project_id):
    project = Project.objects.get(pk=project_id, owner=user)
    return TimeEntry.objects.create(
        user=user,
        project=project,
        date=timezone.localdate(),
        start_time=timezone.now()
    )

# Função para finalizar uma entrada de tempo (TimeEntry)
def stop_entry(user, entry_id):
    entry = TimeEntry.objects.get(pk=entry_id, user=user)
    entry.end_time = timezone.now()
    entry.save()
    return entry
