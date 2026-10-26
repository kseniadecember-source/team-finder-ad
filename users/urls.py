from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("register", views.register_view),
    path("login/", views.login_view, name="login"),
    path("login", views.login_view),
    path("logout/", views.logout_view, name="logout"),
    path("logout", views.logout_view),
    path("list/", views.participants_list_view, name="list"),
    path("list", views.participants_list_view),
    path("edit-profile/", views.edit_profile_view, name="edit_profile"),
    path("edit-profile", views.edit_profile_view),
    path(
        "change-password/",
        views.change_password_view,
        name="change_password",
    ),
    path("change-password", views.change_password_view),
    path("<int:user_id>/", views.user_detail_view, name="detail"),
    path("<int:user_id>", views.user_detail_view),
]
