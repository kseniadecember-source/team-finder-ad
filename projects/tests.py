from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Project

User = get_user_model()


class ProjectsViewsTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password=self.password,
            name="Олег",
            surname="Орлов",
            phone="+79990001122",
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            password=self.password,
            name="Мария",
            surname="Миронова",
            phone="+79990001133",
        )
        self.project = Project.objects.create(
            name="Стартовый проект",
            description="Описание стартового проекта",
            owner=self.owner,
            github_url="https://github.com/owner/repo",
            status=Project.STATUS_OPEN,
        )
        self.project.participants.add(self.owner)

    def test_root_redirects_to_projects_list(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/projects/list", response.url)

    def test_create_project_adds_owner_to_participants(self):
        self.client.login(email="owner@example.com", password=self.password)
        response = self.client.post(
            "/projects/create-project/",
            data={
                "name": "Новый проект",
                "description": "Описание нового проекта",
                "github_url": "https://github.com/owner/new-repo",
                "status": Project.STATUS_OPEN,
            },
        )
        self.assertEqual(response.status_code, 302)
        created = Project.objects.get(name="Новый проект")
        self.assertEqual(created.owner, self.owner)
        self.assertIn(self.owner, created.participants.all())

    def test_edit_project_forbidden_for_non_owner(self):
        self.client.login(email="other@example.com", password=self.password)
        response = self.client.post(
            f"/projects/{self.project.id}/edit/",
            data={
                "name": "Взлом",
                "description": "Описание",
                "github_url": "",
                "status": Project.STATUS_OPEN,
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_complete_project_by_owner(self):
        self.client.login(email="owner@example.com", password=self.password)
        response = self.client.post(f"/projects/{self.project.id}/complete/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "project_status": "closed"},
        )
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.STATUS_CLOSED)

    def test_toggle_participate_and_favorite(self):
        self.client.login(email="other@example.com", password=self.password)

        # Участие в проекте
        resp_part = self.client.post(
            f"/projects/{self.project.id}/toggle-participate/"
        )
        self.assertEqual(resp_part.status_code, 200)
        self.assertTrue(resp_part.json()["participant"])
        self.assertIn(self.other, self.project.participants.all())

        # Избранное
        resp_fav = self.client.post(
            f"/projects/{self.project.id}/toggle-favorite/"
        )
        self.assertEqual(resp_fav.status_code, 200)
        self.assertTrue(resp_fav.json()["favorited"])
        self.assertIn(self.project, self.other.favorites.all())

        fav_page = self.client.get("/projects/favorites/")
        self.assertEqual(fav_page.status_code, 200)
        self.assertIn(self.project, list(fav_page.context["projects"]))
