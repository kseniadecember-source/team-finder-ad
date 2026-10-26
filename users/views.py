from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EditProfileForm, LoginForm, RegisterForm

User = get_user_model()

USERS_PER_PAGE = 12


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:login")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip()
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            if user is None:
                user_obj = User.objects.filter(email__iexact=email).first()
                if user_obj is not None:
                    user = authenticate(
                        request,
                        email=user_obj.email,
                        password=password,
                    )
            if user is not None:
                login(request, user)
                return redirect("/projects/list/")
            form.add_error(None, "Неверный email или пароль")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("/projects/list/")


def participants_list_view(request):
    qs = User.objects.all().order_by("-id")
    active_filter = request.GET.get("filter", "").strip()

    if request.user.is_authenticated and active_filter:
        if active_filter == "owners-of-favorite-projects":
            qs = (
                User.objects.filter(
                    owned_projects__interested_users=request.user
                )
                .distinct()
                .order_by("-id")
            )
        elif active_filter == "owners-of-participating-projects":
            qs = (
                User.objects.filter(owned_projects__participants=request.user)
                .distinct()
                .order_by("-id")
            )
        elif active_filter == "interested-in-my-projects":
            qs = (
                User.objects.filter(favorites__owner=request.user)
                .distinct()
                .order_by("-id")
            )
        elif active_filter == "participants-of-my-projects":
            qs = (
                User.objects.filter(participated_projects__owner=request.user)
                .distinct()
                .order_by("-id")
            )
        else:
            active_filter = ""
    else:
        active_filter = ""

    paginator = Paginator(qs, USERS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    query_prefix = f"filter={active_filter}&" if active_filter else ""

    context = {
        "participants": page_obj,
        "page_obj": page_obj,
        "active_filter": active_filter,
        "query_prefix": query_prefix,
    }
    return render(request, "users/participants.html", context)


def user_detail_view(request, user_id):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("owned_projects__participants"),
        pk=user_id,
    )
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = EditProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )
        if form.is_valid():
            form.save()
            return redirect(f"/users/{request.user.id}/")
    else:
        form = EditProfileForm(instance=request.user)
    return render(
        request,
        "users/edit_profile.html",
        {"form": form, "from": form, "user": request.user},
    )


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(f"/users/{request.user.id}/")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(
        request,
        "users/change_password.html",
        {"form": form, "from": form},
    )
