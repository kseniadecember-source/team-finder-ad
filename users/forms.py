import re
from urllib.parse import urlparse

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


def validate_github_url(url):
    """Проверяет, что переданная ссылка ведёт на github.com."""
    if not url:
        return url
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https") or parsed.netloc.lower() not in (
        "github.com",
        "www.github.com",
    ):
        raise forms.ValidationError(
            "Ссылка должна быть валидной и вести на сайт github.com."
        )
    return url.strip()


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "Ссылка на GitHub",
        }
        widgets = {
            "avatar": forms.FileInput(
                attrs={"id": "id_avatar", "accept": "image/*"}
            ),
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone:
            return ""
        if not re.fullmatch(r"(\+7|8)\d{10}", phone):
            raise forms.ValidationError(
                "Номер телефона должен быть в формате +7XXXXXXXXXX "
                "или 8XXXXXXXXXX."
            )
        digits = phone[-10:]
        normalized_plus7 = f"+7{digits}"
        normalized_8 = f"8{digits}"
        qs = User.objects.filter(phone__in=[normalized_plus7, normalized_8])
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "Пользователь с таким номером телефона уже существует."
            )
        return normalized_plus7

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url") or ""
        return validate_github_url(url)
