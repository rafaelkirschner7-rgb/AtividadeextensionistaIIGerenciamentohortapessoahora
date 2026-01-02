from django.contrib import admin
from .models import Project, TimeEntry

# Registra o modelo Project no painel de administração 
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('name', 'description')

# Registra o modelo TimeEntry no painel de administração
@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'date', 'start_time', 'end_time')
    list_filter = ('project', 'date')
    search_fields = ('notes',)


