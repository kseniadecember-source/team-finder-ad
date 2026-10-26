from django import forms

from users.forms import validate_github_url

from .models import Project


class ProjectForm(forms.ModelForm):
    STATUS_FORM_CHOICES = [
        (Project.STATUS_OPEN, "Открыт"),
        (Project.STATUS_CLOSED, "Закрыт"),
    ]

    status = forms.ChoiceField(
        choices=STATUS_FORM_CHOICES,
        label="Статус проекта",
        initial=Project.STATUS_OPEN,
    )

    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус проекта",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url") or ""
        return validate_github_url(url)
