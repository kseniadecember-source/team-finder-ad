from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from projects import views as project_views


def root_redirect(request):
    return redirect("/projects/list/")


urlpatterns = [
    path("", root_redirect, name="root"),
    path("admin/", admin.site.urls),
    path("users/", include("users.urls", namespace="users")),
    path("projects/", include("projects.urls", namespace="projects")),
    path("project/", include(("projects.urls", "projects"), namespace="project")),
    path(
        "<int:project_id>/toggle-favorite/",
        project_views.toggle_favorite_view,
    ),
    path(
        "<int:project_id>/toggle-favorite",
        project_views.toggle_favorite_view,
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
