from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("list/", views.project_list_view, name="list"),
    path("list", views.project_list_view),
    path("favorites/", views.favorite_projects_view, name="favorites"),
    path("favorites", views.favorite_projects_view),
    path("create-project/", views.create_project_view, name="create"),
    path("create-project", views.create_project_view),
    path("<int:project_id>/", views.project_detail_view, name="detail"),
    path("<int:project_id>", views.project_detail_view),
    path("<int:project_id>/edit/", views.edit_project_view, name="edit"),
    path("<int:project_id>/edit", views.edit_project_view),
    path(
        "<int:project_id>/complete/",
        views.complete_project_view,
        name="complete",
    ),
    path("<int:project_id>/complete", views.complete_project_view),
    path(
        "<int:project_id>/toggle-participate/",
        views.toggle_participate_view,
        name="toggle_participate",
    ),
    path(
        "<int:project_id>/toggle-participate",
        views.toggle_participate_view,
    ),
    path(
        "<int:project_id>/toggle-favorite/",
        views.toggle_favorite_view,
        name="toggle_favorite",
    ),
    path("<int:project_id>/toggle-favorite", views.toggle_favorite_view),
]
