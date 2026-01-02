from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F, ExpressionWrapper, DurationField
from .models import Project, TimeEntry
from .forms import ProjectForm, TimeEntryForm
from .services import start_entry, stop_entry
from django.contrib.auth.models import User
from django.utils import timezone


# ============================
# DASHBOARD
# ============================
@login_required
def dashboard(request):
    # Lista projetos ativos do usuário logado
    projects = Project.objects.filter(owner=request.user, active=True)
    
    # Verifica se há uma entrada de tempo em andamento (sem end_time)
    running = TimeEntry.objects.filter(user=request.user, end_time__isnull=True).first()

    # Captura filtros GET opcionais (datas)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Entradas finalizadas do usuário
    entries = TimeEntry.objects.filter(user=request.user, end_time__isnull=False)
    if start_date:
        entries = entries.filter(date__gte=start_date)
    if end_date:
        entries = entries.filter(date__lte=end_date)

    # Soma total de horas das entradas filtradas
    total_hours = sum(e.duration_hours() for e in entries)

    # Contexto enviado ao template
    context = {
        'projects': projects,
        'running': running,
        'total_hours': total_hours,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'timesheet/dashboard.html', context)


# ============================
# PROJETOS (CRUD)
# ============================
@login_required
def project_list(request):
    # Lista todos os projetos do usuário logado
    projects = Project.objects.filter(owner=request.user)
    return render(request, 'timesheet/project_list.html', {'projects': projects})

@login_required
def project_create(request):
    # Criação de novo projeto
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            proj = form.save(commit=False)
            proj.owner = request.user  # garante que o dono é o usuário logado
            proj.save()
            return redirect('timesheet:project_list')
    else:
        form = ProjectForm()
    return render(request, 'timesheet/project_form.html', {'form': form, 'title': 'Novo Projeto'})

@login_required
def project_update(request, pk):
    # Edição de projeto existente
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('timesheet:project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'timesheet/project_form.html', {'form': form, 'title': 'Editar Projeto'})


# ============================
# ENTRADAS DE TEMPO (CRUD)
# ============================
@login_required
def entry_list(request):
    # Lista todas as entradas do usuário logado
    entries = TimeEntry.objects.filter(user=request.user)
    return render(request, 'timesheet/entry_list.html', {'entries': entries})

@login_required
def entry_create(request):
    # Criação de nova entrada
    if request.method == 'POST':
        form = TimeEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user  # vincula ao usuário logado
            entry.save()
            return redirect('timesheet:entry_list')
    else:
        form = TimeEntryForm()
    return render(request, 'timesheet/entry_form.html', {'form': form, 'title': 'Nova Entrada'})

@login_required
def entry_update(request, pk):
    # Edição de entrada existente
    entry = get_object_or_404(TimeEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TimeEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('timesheet:entry_list')
    else:
        form = TimeEntryForm(instance=entry)
    return render(request, 'timesheet/entry_form.html', {'form': form, 'title': 'Editar Entrada'})

@login_required
def entry_delete(request, pk):
    # Exclusão de entrada
    entry = get_object_or_404(TimeEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        entry.delete()
        return redirect('timesheet:entry_list')
    return render(request, 'timesheet/entry_form.html', {'form': None, 'title': 'Excluir Entrada'})


# ============================
# INÍCIO / FIM DE ENTRADAS
# ============================
@login_required
def entry_start(request, project_id):
    # Inicia uma entrada de tempo para o projeto
    start_entry(request.user, project_id)
    return redirect('timesheet:dashboard')

@login_required
def entry_stop(request, entry_id):
    # Finaliza uma entrada de tempo existente
    stop_entry(request.user, entry_id)
    return redirect('timesheet:dashboard')


# ============================
# RELATÓRIOS
# ============================
@login_required
def report_view(request):
    # Entradas finalizadas do usuário
    qs = TimeEntry.objects.filter(user=request.user, end_time__isnull=False)
    total_hours = sum(e.duration_hours() for e in qs)

    # Soma horas por projeto
    by_project = {}
    for e in qs:
        by_project.setdefault(e.project.name, 0)
        by_project[e.project.name] += e.duration_hours()

    context = {
        'total_hours': total_hours,
        'by_project': by_project,
        'entries': qs,
    }
    return render(request, 'timesheet/report.html', context)


@login_required
def total_hours_by_user(request):
    # Filtros GET opcionais (YYYY-MM-DD)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    users = User.objects.all()
    data = []
    for u in users:
        # Entradas finalizadas por usuário
        entries = TimeEntry.objects.filter(user=u, end_time__isnull=False)
        if start_date:
            entries = entries.filter(date__gte=start_date)
        if end_date:
            entries = entries.filter(date__lte=end_date)
        total = sum(e.duration_hours() for e in entries)
        data.append({'user': u, 'total_hours': total})

    return render(request, 'timesheet/total_hours.html', {
        'data': data,
        'start_date': start_date,
        'end_date': end_date,
    })


@login_required
def report_total_hours(request):
    # Filtros GET opcionais (YYYY-MM-DD)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Base: entradas com end_time preenchido
    qs = TimeEntry.objects.filter(end_time__isnull=False)

    # Filtrar por data do start_time
    if start_date:
        qs = qs.filter(start_time__date__gte=start_date)
    if end_date:
        qs = qs.filter(start_time__date__lte=end_date)

    # Expressão para calcular duração (end_time - start_time)
    duration_expr = ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())

    # Somar por usuário
    totals = (
        qs.values('user__id', 'user__username')
          .annotate(total_duration=Sum(duration_expr))
          .order_by('user__username')
    )

    # Converter timedelta em horas (float) para mostrar no template
    data = []
    for row in totals:
        td = row['total_duration']
        hours = td.total_seconds() / 3600 if td else 0
        data.append({'username': row['user__username'], 'total_hours': round(hours, 2)})

    return render(request, 'timesheet/report_total_hours.html', {
        'data': data,
        'start_date': start_date,
        'end_date': end_date,
    })