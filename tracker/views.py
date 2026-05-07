from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json
from .models import Project, Session, Event

def dashboard(request):
    projects = Project.objects.all()
    today = timezone.now().date()
    heatmap_data = {}
    for i in range(365):
        heatmap_data[str(today - timedelta(days=i))] = 0
    sessions = Session.objects.filter(ended_at__isnull=False)
    for s in sessions:
        d = str(s.started_at.date())
        if d in heatmap_data: heatmap_data[d] += s.useful_seconds
    today_sessions = sessions.filter(started_at__date=today)
    week_sessions = sessions.filter(started_at__date__gte=today-timedelta(days=7))
    return render(request, 'tracker/dashboard.html', {
        'projects': projects,
        'heatmap_data': json.dumps(heatmap_data),
        'today_seconds': sum(s.useful_seconds for s in today_sessions),
        'week_seconds': sum(s.useful_seconds for s in week_sessions),
        'all_seconds': sum(s.useful_seconds for s in sessions),
        'active_session': Session.objects.filter(ended_at__isnull=True).first(),
        'project_data': json.dumps([{'name':p.name,'seconds':p.total_seconds,'color':p.color,'sessions':p.total_sessions} for p in projects if p.total_seconds>0]),
        'recent_sessions': sessions.order_by('-started_at')[:10],
    })

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    sessions = project.sessions.filter(ended_at__isnull=False).order_by('-started_at')
    today = timezone.now().date()
    heatmap_data = {}
    for i in range(365):
        heatmap_data[str(today - timedelta(days=i))] = 0
    for s in sessions:
        d = str(s.started_at.date())
        if d in heatmap_data: heatmap_data[d] += s.useful_seconds
    return render(request, 'tracker/project_detail.html', {
        'project': project, 'sessions': sessions[:20],
        'heatmap_data': json.dumps(heatmap_data),
        'total_coding': sum(s.coding_seconds for s in sessions),
        'total_testing': sum(s.testing_seconds for s in sessions),
    })

def project_edit(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        project.name = request.POST.get('name', project.name)
        project.description = request.POST.get('description', project.description)
        project.language = request.POST.get('language', project.language)
        project.color = request.POST.get('color', project.color)
        project.path = request.POST.get('path', project.path)
        project.save()
        return redirect('project_detail', slug=project.slug)
    return render(request, 'tracker/project_edit.html', {'project': project})

def projects_list(request):
    projects = Project.objects.all()
    data = [{'name':p.name,'slug':p.slug,'description':p.description,'language':p.language,'color':p.color,'seconds':p.total_seconds,'sessions':p.total_sessions} for p in projects]
    return render(request, 'tracker/projects.html', {'projects': projects, 'project_data': json.dumps(data)})

@csrf_exempt
def api_new_project(request):
    if request.method != 'POST': return JsonResponse({'error':'POST required'},status=405)
    data = json.loads(request.body)
    name = data.get('name','').strip()
    if not name: return JsonResponse({'error':'name required'},status=400)
    from django.utils.text import slugify
    slug = slugify(name)
    project, created = Project.objects.get_or_create(slug=slug, defaults={'name':name,'path':data.get('path','')})
    return JsonResponse({'id':project.id,'name':project.name,'slug':project.slug,'created':created})

@csrf_exempt
def api_start_session(request):
    if request.method != 'POST': return JsonResponse({'error':'POST required'},status=405)
    data = json.loads(request.body)
    slug = data.get('slug','').strip()
    try: project = Project.objects.get(slug=slug)
    except Project.DoesNotExist: return JsonResponse({'error':f'Projeto "{slug}" não encontrado. Rode: new-project {slug}'},status=404)
    if data.get('path'): project.path=data['path']; project.save()
    auto_closed = []
    for s in Session.objects.filter(ended_at__isnull=True):
        s.ended_at=timezone.now(); s.auto_closed=True; s.save()
        Event.objects.create(session=s, event_type='session_end', metadata={'auto_closed':True})
        auto_closed.append(s.project.name)
    session = Session.objects.create(project=project)
    Event.objects.create(session=session, event_type='session_start')
    return JsonResponse({'session_id':session.id,'project':project.name,'started_at':session.started_at.isoformat(),'auto_closed':auto_closed})

@csrf_exempt
def api_run_server(request):
    if request.method != 'POST': return JsonResponse({'error':'POST required'},status=405)
    session = Session.objects.filter(ended_at__isnull=True).first()
    if not session: return JsonResponse({'error':'Nenhuma sessão ativa. Rode: start-session'},status=400)
    Event.objects.create(session=session, event_type='server_start')
    return JsonResponse({'ok':True,'session_id':session.id,'project':session.project.name})

@csrf_exempt
def api_stop_server(request):
    if request.method != 'POST': return JsonResponse({'error':'POST required'},status=405)
    session = Session.objects.filter(ended_at__isnull=True).first()
    if not session: return JsonResponse({'error':'Nenhuma sessão ativa.'},status=400)
    Event.objects.create(session=session, event_type='server_stop')
    return JsonResponse({'ok':True,'session_id':session.id})

@csrf_exempt
def api_end_session(request):
    if request.method != 'POST': return JsonResponse({'error':'POST required'},status=405)
    session = Session.objects.filter(ended_at__isnull=True).first()
    if not session: return JsonResponse({'error':'Nenhuma sessão ativa.'},status=400)
    session.ended_at = timezone.now()
    notes = json.loads(request.body).get('notes','')
    if notes: session.notes = notes
    session.save()
    Event.objects.create(session=session, event_type='session_end')
    return JsonResponse({'ok':True,'project':session.project.name,'started_at':session.started_at.isoformat(),
        'ended_at':session.ended_at.isoformat(),'total_seconds':session.total_seconds,
        'coding_seconds':session.coding_seconds,'testing_seconds':session.testing_seconds,'useful_seconds':session.useful_seconds})

def api_status(request):
    session = Session.objects.filter(ended_at__isnull=True).first()
    if not session: return JsonResponse({'active':False})
    last_event = session.events.last()
    return JsonResponse({'active':True,'session_id':session.id,'project':session.project.name,
        'started_at':session.started_at.isoformat(),'elapsed_seconds':session.total_seconds,
        'in_test_mode': last_event and last_event.event_type=='server_start'})
