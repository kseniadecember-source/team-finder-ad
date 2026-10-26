from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project

PROJECTS_PER_PAGE = 12


def project_list_view(request):
    projects_qs = (
        Project.objects.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    paginator = Paginator(projects_qs, PROJECTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "projects": page_obj,
        "page_obj": page_obj,
        "query_prefix": "",
    }
    return render(request, "projects/project_list.html", context)


@login_required
def favorite_projects_view(request):
    projects_qs = (
        request.user.favorites.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    return render(
        request,
        "projects/favorite_projects.html",
        {"projects": projects_qs},
    )


def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related(
            "participants"
        ),
        pk=project_id,
    )
    return render(
        request,
        "projects/project-details.html",
        {"project": project},
    )


@login_required
def create_project_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f"/projects/{project.id}/")
    else:
        form = ProjectForm()
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Недостаточно прав для редактирования.")

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            return redirect(f"/projects/{project.id}/")
    else:
        form = ProjectForm(instance=project)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True, "project": project},
    )


@require_POST
def complete_project_view(request, project_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "error", "detail": "Authentication required"},
            status=401,
        )
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse(
            {"status": "error", "detail": "Forbidden"},
            status=403,
        )
    if project.status != Project.STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "detail": "Project already closed"},
            status=400,
        )
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": "closed"})


@require_POST
def toggle_participate_view(request, project_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "error", "detail": "Authentication required"},
            status=401,
        )
    project = get_object_or_404(Project, pk=project_id)
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        is_participant = False
    else:
        project.participants.add(request.user)
        is_participant = True
    return JsonResponse({"status": "ok", "participant": is_participant})


@require_POST
def toggle_favorite_view(request, project_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "error", "detail": "Authentication required"},
            status=401,
        )
    project = get_object_or_404(Project, pk=project_id)
    if request.user.favorites.filter(pk=project.pk).exists():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})
