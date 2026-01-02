from django.urls import path
from . import views

app_name = 'timesheet'

# Lista de padrões de URL da aplicação
urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('projects/', views.project_list, name='project_list'),
    path('projects/new/', views.project_create, name='project_create'),
    path('projects/<int:pk>/edit/', views.project_update, name='project_update'),

    path('entries/', views.entry_list, name='entry_list'),
    path('entries/new/', views.entry_create, name='entry_create'),
    path('entries/<int:pk>/edit/', views.entry_update, name='entry_update'),
    path('entries/<int:pk>/delete/', views.entry_delete, name='entry_delete'),

    path('report/', views.report_view, name='report'),
    path('start/<int:project_id>/', views.entry_start, name='entry_start'),
    path('stop/<int:entry_id>/', views.entry_stop, name='entry_stop'),
    path('users/hours/', views.total_hours_by_user, name='total_hours_by_user'),
    path('users/hours/', views.total_hours_by_user, name='total_hours_by_user'),
    path('report/users/', views.report_total_hours, name='report_total_hours'),
   

]
