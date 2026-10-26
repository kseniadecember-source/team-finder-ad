from django.contrib.auth import get_user_model
from django.test import TestCase

from projects.models import Project

User = get_user_model()


class UsersViewsTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password=self.password,
            name="Иван",
            surname="Иванов",
            phone="+79991112233",
            github_url="https://github.com/ivan",
            about="Backend developer",
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password=self.password,
            name="Анна",
            surname="Петрова",
            phone="+79991112244",
            github_url="https://github.com/anna",
            about="Frontend developer",
        )
        self.project1 = Project.objects.create(
            name="Проект Ивана",
            description="Описание 1",
            owner=self.user1,
            status=Project.STATUS_OPEN,
        )
        self.project1.participants.add(self.user1, self.user2)

        self.project2 = Project.objects.create(
            name="Проект Анны",
            description="Описание 2",
            owner=self.user2,
            status=Project.STATUS_OPEN,
        )
        self.project2.participants.add(self.user2)
        self.user1.favorites.add(self.project2)

    def test_avatar_generated_on_create(self):
        self.assertTrue(bool(self.user1.avatar))

    def test_register_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            "/users/register/",
            data={
                "name": "Сергей",
                "surname": "Сидоров",
                "email": "sergey@example.com",
                "password": "NewPassword123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login", response.url)
        self.assertTrue(
            User.objects.filter(email="sergey@example.com").exists()
        )

    def test_login_and_logout(self):
        response = self.client.post(
            "/users/login/",
            data={"email": "user1@example.com", "password": self.password},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/projects/list", response.url)

        logout_resp = self.client.get("/users/logout/")
        self.assertEqual(logout_resp.status_code, 302)

    def test_edit_profile_phone_and_github_validation(self):
        self.client.login(email="user1@example.com", password=self.password)

        # Дубликат телефона в формате 8... (совпадает с +7... у user2)
        resp_dup = self.client.post(
            "/users/edit-profile/",
            data={
                "name": "Иван",
                "surname": "Иванов",
                "about": "Обновлено",
                "phone": "89991112244",
                "github_url": "https://github.com/ivan",
            },
        )
        self.assertEqual(resp_dup.status_code, 200)
        self.assertTrue(resp_dup.context["form"].errors)

        # Невалидная ссылка (не github.com)
        resp_bad_url = self.client.post(
            "/users/edit-profile/",
            data={
                "name": "Иван",
                "surname": "Иванов",
                "about": "Обновлено",
                "phone": "89995556677",
                "github_url": "https://example.com/ivan",
            },
        )
        self.assertEqual(resp_bad_url.status_code, 200)
        self.assertTrue(resp_bad_url.context["form"].errors)

        # Валидное обновление
        resp_ok = self.client.post(
            "/users/edit-profile/",
            data={
                "name": "Иван",
                "surname": "Иванов",
                "about": "Обновлено",
                "phone": "89995556677",
                "github_url": "https://github.com/ivan-new",
            },
        )
        self.assertEqual(resp_ok.status_code, 302)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.phone, "+79995556677")

    def test_participants_filters_var1(self):
        self.client.login(email="user1@example.com", password=self.password)

        # Авторы избранных проектов для user1 -> user2
        resp1 = self.client.get(
            "/users/list/?filter=owners-of-favorite-projects"
        )
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(list(resp1.context["page_obj"]), [self.user2])

        # Участники моих проектов для user1 -> user1, user2
        resp2 = self.client.get(
            "/users/list/?filter=participants-of-my-projects"
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertIn(self.user2, list(resp2.context["page_obj"]))
