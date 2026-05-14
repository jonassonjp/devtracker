import json
import re
from datetime import datetime, time, timedelta

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt

from .models import Event, Project, Session


def _unique_slug(name, exclude_id=None):
    base = slugify(name)
    slug, counter = base, 1
    qs = Project.objects.exclude(id=exclude_id) if exclude_id else Project.objects
    while qs.filter(slug=slug).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def dashboard(request):
    projects = Project.objects.all()
    today = timezone.localdate()
    heatmap_data = {}
    for i in range(365):
        heatmap_data[str(today - timedelta(days=i))] = 0
    sessions = Session.objects.filter(ended_at__isnull=False)
    for s in sessions:
        d = str(timezone.localtime(s.started_at).date())
        if d in heatmap_data:
            heatmap_data[d] += s.useful_seconds
    day_start = timezone.make_aware(datetime.combine(today, time.min))
    today_sessions = sessions.filter(started_at__gte=day_start, started_at__lt=day_start + timedelta(days=1))
    week_sessions = sessions.filter(started_at__gte=day_start - timedelta(days=6))
    return render(
        request,
        "tracker/dashboard.html",
        {
            "projects": projects,
            "heatmap_data": json.dumps(heatmap_data),
            "today_seconds": sum(s.useful_seconds for s in today_sessions),
            "week_seconds": sum(s.useful_seconds for s in week_sessions),
            "all_seconds": sum(s.useful_seconds for s in sessions),
            "active_session": Session.objects.filter(ended_at__isnull=True).first(),
            "project_data": json.dumps(
                [
                    {
                        "name": p.name,
                        "slug": p.slug,
                        "seconds": p.total_seconds,
                        "color": p.color,
                        "sessions": p.total_sessions,
                    }
                    for p in projects
                    if p.total_seconds > 0
                ]
            ),
            "recent_sessions": sessions.order_by("-started_at")[:10],
        },
    )


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    sessions = project.sessions.filter(ended_at__isnull=False).order_by("-started_at")
    today = timezone.localdate()
    heatmap_data = {}
    for i in range(365):
        heatmap_data[str(today - timedelta(days=i))] = 0
    for s in sessions:
        d = str(timezone.localtime(s.started_at).date())
        if d in heatmap_data:
            heatmap_data[d] += s.useful_seconds
    return render(
        request,
        "tracker/project_detail.html",
        {
            "project": project,
            "sessions": sessions[:20],
            "heatmap_data": json.dumps(heatmap_data),
            "total_coding": sum(s.coding_seconds for s in sessions),
            "total_testing": sum(s.testing_seconds for s in sessions),
        },
    )


def project_edit(request, slug):
    project = get_object_or_404(Project, slug=slug)
    errors = {}
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        nickname = request.POST.get("nickname", "").strip()
        description = request.POST.get("description", project.description)
        language = request.POST.get("language", project.language)
        color = request.POST.get("color", project.color)
        path = request.POST.get("path", project.path)

        if not name:
            errors["name"] = "Nome é obrigatório."
        elif Project.objects.exclude(id=project.id).filter(name=name).exists():
            errors["name"] = f'Já existe um projeto com o nome "{name}".'

        if nickname:
            if not re.match(r"^[a-zA-Z0-9_-]+$", nickname):
                errors["nickname"] = (
                    "Apelido não pode conter espaços ou caracteres especiais."
                )
            elif (
                Project.objects.exclude(id=project.id)
                .filter(nickname=nickname)
                .exists()
            ):
                errors["nickname"] = f'Apelido "{nickname}" já está em uso.'

        if not errors:
            if name != project.name:
                project.slug = _unique_slug(name, exclude_id=project.id)
            project.name = name
            project.nickname = nickname or None
            project.description = description
            project.language = language
            project.color = color
            project.path = path
            project.save()
            return redirect("project_detail", slug=project.slug)

        # re-render with submitted values and errors
        project.name = name
        project.nickname = nickname
        project.description = description
        project.language = language
        project.color = color
        project.path = path

    return render(
        request, "tracker/project_edit.html", {"project": project, "errors": errors}
    )


def projects_list(request):
    projects = Project.objects.all()
    data = [
        {
            "name": p.name,
            "slug": p.slug,
            "description": p.description,
            "language": p.language,
            "color": p.color,
            "seconds": p.total_seconds,
            "sessions": p.total_sessions,
        }
        for p in projects
    ]
    return render(
        request,
        "tracker/projects.html",
        {"projects": projects, "project_data": json.dumps(data)},
    )


@csrf_exempt
def api_new_project(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    data = json.loads(request.body)
    name = data.get("name", "").strip()
    if not name:
        return JsonResponse({"error": "name required"}, status=400)
    from django.utils.text import slugify

    slug = slugify(name)
    project, created = Project.objects.get_or_create(
        slug=slug, defaults={"name": name, "path": data.get("path", "")}
    )
    return JsonResponse(
        {
            "id": project.id,
            "name": project.name,
            "slug": project.slug,
            "created": created,
        }
    )


@csrf_exempt
def api_start_session(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    data = json.loads(request.body)
    slug = data.get("slug", "").strip()
    try:
        project = Project.objects.get(slug=slug)
    except Project.DoesNotExist:
        return JsonResponse(
            {"error": f'Projeto "{slug}" não encontrado. Rode: new-project {slug}'},
            status=404,
        )
    if data.get("path"):
        project.path = data["path"]
        project.save()
    auto_closed = []
    for s in Session.objects.filter(ended_at__isnull=True):
        s.ended_at = timezone.now()
        s.auto_closed = True
        s.save()
        Event.objects.create(
            session=s, event_type="session_end", metadata={"auto_closed": True}
        )
        auto_closed.append(s.project.name)
    session = Session.objects.create(project=project)
    Event.objects.create(session=session, event_type="session_start")
    return JsonResponse(
        {
            "session_id": session.id,
            "project": project.name,
            "started_at": session.started_at.isoformat(),
            "auto_closed": auto_closed,
        }
    )


@csrf_exempt
def api_run_server(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    session = Session.objects.filter(ended_at__isnull=True).first()
    if not session:
        return JsonResponse(
            {"error": "Nenhuma sessão ativa. Rode: start-session"}, status=400
        )
    Event.objects.create(session=session, event_type="server_start")
    return JsonResponse(
        {"ok": True, "session_id": session.id, "project": session.project.name}
    )


@csrf_exempt
def api_stop_server(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    session = Session.objects.filter(ended_at__isnull=True).first()
    if not session:
        return JsonResponse({"error": "Nenhuma sessão ativa."}, status=400)
    Event.objects.create(session=session, event_type="server_stop")
    return JsonResponse({"ok": True, "session_id": session.id})


@csrf_exempt
def api_end_session(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    session = Session.objects.filter(ended_at__isnull=True).first()
    if not session:
        return JsonResponse({"error": "Nenhuma sessão ativa."}, status=400)
    session.ended_at = timezone.now()
    notes = json.loads(request.body).get("notes", "")
    if notes:
        session.notes = notes
    session.save()
    Event.objects.create(session=session, event_type="session_end")
    return JsonResponse(
        {
            "ok": True,
            "project": session.project.name,
            "started_at": session.started_at.isoformat(),
            "ended_at": session.ended_at.isoformat(),
            "total_seconds": session.total_seconds,
            "coding_seconds": session.coding_seconds,
            "testing_seconds": session.testing_seconds,
            "useful_seconds": session.useful_seconds,
        }
    )


def api_day(request):
    date_str = request.GET.get("date", "")
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "date param required (YYYY-MM-DD)"}, status=400)
    day_start = timezone.make_aware(datetime.combine(date, time.min))
    day_end = day_start + timedelta(days=1)
    sessions = (
        Session.objects.filter(ended_at__isnull=False, started_at__gte=day_start, started_at__lt=day_end)
        .select_related("project")
        .order_by("started_at")
    )
    data = []
    for s in sessions:
        local_start = timezone.localtime(s.started_at)
        local_end = timezone.localtime(s.ended_at)
        data.append({
            "id": s.id,
            "project": s.project.name,
            "project_slug": s.project.slug,
            "project_color": s.project.color,
            "started_at": local_start.strftime("%H:%M"),
            "ended_at": local_end.strftime("%H:%M"),
            "coding_seconds": s.coding_seconds,
            "testing_seconds": s.testing_seconds,
            "useful_seconds": s.useful_seconds,
            "notes": s.notes,
        })
    total_useful = sum(s.useful_seconds for s in sessions)
    return JsonResponse({"date": date_str, "total_useful": total_useful, "sessions": data})


def api_status(request):
    session = Session.objects.filter(ended_at__isnull=True).first()
    if not session:
        return JsonResponse({"active": False})
    last_event = session.events.last()
    return JsonResponse(
        {
            "active": True,
            "session_id": session.id,
            "project": session.project.name,
            "started_at": session.started_at.isoformat(),
            "elapsed_seconds": session.total_seconds,
            "in_test_mode": last_event and last_event.event_type == "server_start",
        }
    )
