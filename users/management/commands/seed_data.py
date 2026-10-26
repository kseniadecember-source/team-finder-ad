from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from projects.models import Project

User = get_user_model()

TEST_USERS = [
    {
        "email": "admin@teamfinder.ru",
        "password": "AdminPassword123!",
        "name": "Ксения",
        "surname": "Декабрьская",
        "phone": "+79990000001",
        "github_url": "https://github.com/kseniadecember-source",
        "about": "Fullstack-разработчик и администратор платформы TeamFinder.",
        "is_staff": True,
        "is_superuser": True,
        "projects": [
            {
                "name": "TeamFinder Platform",
                "description": (
                    "Платформа для поиска команды и единомышленников для "
                    "совместной разработки Pet-проектов на Django и PostgreSQL."
                ),
                "github_url": (
                    "https://github.com/kseniadecember-source/team-finder-ad"
                ),
                "status": Project.STATUS_OPEN,
            },
        ],
    },
    {
        "email": "alexey@teamfinder.ru",
        "password": "UserPassword123!",
        "name": "Алексей",
        "surname": "Смирнов",
        "phone": "+79990000002",
        "github_url": "https://github.com/alexey-dev",
        "about": (
            "Backend-разработчик на Python (Django, FastAPI, PostgreSQL). "
            "Интересуюсь микросервисной архитектурой и ML."
        ),
        "is_staff": False,
        "is_superuser": False,
        "projects": [
            {
                "name": "AI Code Review Assistant",
                "description": (
                    "Бот для автоматического ревью пул-реквестов на GitHub "
                    "с проверкой архитектуры, безопасности и стиля кода."
                ),
                "github_url": "https://github.com/alexey-dev/ai-code-review",
                "status": Project.STATUS_OPEN,
            },
            {
                "name": "Async Task Tracker",
                "description": (
                    "Трекер задач для небольших распределённых команд "
                    "с уведомлениями в Telegram и канбан-доской."
                ),
                "github_url": "https://github.com/alexey-dev/task-tracker",
                "status": Project.STATUS_OPEN,
            },
        ],
    },
    {
        "email": "maria@teamfinder.ru",
        "password": "UserPassword123!",
        "name": "Мария",
        "surname": "Соколова",
        "phone": "+79990000003",
        "github_url": "https://github.com/maria-ui",
        "about": (
            "Frontend-разработчик и UI/UX дизайнер. Проектирую удобные "
            "интерфейсы на React и TypeScript."
        ),
        "is_staff": False,
        "is_superuser": False,
        "projects": [
            {
                "name": "Design System UI Kit",
                "description": (
                    "Открытая библиотека доступных компонентов и дизайн-система "
                    "для быстрой сборки современных веб-приложений."
                ),
                "github_url": "https://github.com/maria-ui/design-system-kit",
                "status": Project.STATUS_OPEN,
            },
        ],
    },
    {
        "email": "dmitry@teamfinder.ru",
        "password": "UserPassword123!",
        "name": "Дмитрий",
        "surname": "Волков",
        "phone": "+79990000004",
        "github_url": "https://github.com/dmitry-data",
        "about": (
            "Data Engineer и аналитик данных. Работаю с Airflow, ClickHouse "
            "и визуализацией метрик."
        ),
        "is_staff": False,
        "is_superuser": False,
        "projects": [
            {
                "name": "Open Weather Analytics",
                "description": (
                    "Сервис сбора и визуализации погодных аномалий и "
                    "климатических трендов по открытым метеоданным."
                ),
                "github_url": "https://github.com/dmitry-data/weather-analytics",
                "status": Project.STATUS_OPEN,
            },
        ],
    },
    {
        "email": "elena@teamfinder.ru",
        "password": "UserPassword123!",
        "name": "Елена",
        "surname": "Морозова",
        "phone": "+79990000005",
        "github_url": "https://github.com/elena-qa",
        "about": (
            "QA Automation Engineer (Pytest, Playwright). Помогаю командам "
            "выстраивать надёжные пайплайны тестирования."
        ),
        "is_staff": False,
        "is_superuser": False,
        "projects": [
            {
                "name": "E2E Test Runner Dashboard",
                "description": (
                    "Панель мониторинга результатов автотестов с историей "
                    "падений, скриншотами и интеграцией с CI/CD."
                ),
                "github_url": "https://github.com/elena-qa/e2e-dashboard",
                "status": Project.STATUS_CLOSED,
            },
        ],
    },
]


def seed_initial_data():
    """Создаёт тестовых пользователей, проекты, участников и избранное."""
    created_users = []
    created_projects = []

    for item in TEST_USERS:
        user = User.objects.filter(email=item["email"]).first()
        if user is None:
            user = User.objects.create_user(
                email=item["email"],
                password=item["password"],
                name=item["name"],
                surname=item["surname"],
                phone=item["phone"],
                github_url=item["github_url"],
                about=item["about"],
                is_staff=item["is_staff"],
                is_superuser=item["is_superuser"],
            )
        elif not user.avatar or not user.avatar.storage.exists(
            user.avatar.name
        ):
            user.avatar = None
            user.save()
        created_users.append(user)

        for proj_data in item["projects"]:
            project, _ = Project.objects.get_or_create(
                name=proj_data["name"],
                owner=user,
                defaults={
                    "description": proj_data["description"],
                    "github_url": proj_data["github_url"],
                    "status": proj_data["status"],
                },
            )
            project.participants.add(user)
            created_projects.append(project)

    if len(created_users) >= 4 and len(created_projects) >= 4:
        u0, u1, u2, u3 = created_users[:4]
        p0, p1, p2, p3 = created_projects[:4]

        p0.participants.add(u1, u2)
        p1.participants.add(u0, u3)
        p2.participants.add(u0, u1)

        u0.favorites.add(p1, p2)
        u1.favorites.add(p0, p3)
        u2.favorites.add(p0, p1)
        u3.favorites.add(p0, p2)

    return len(created_users), len(created_projects)


class Command(BaseCommand):
    help = "Заполняет базу данных тестовыми пользователями и проектами."

    def handle(self, *args, **options):
        users_count, projects_count = seed_initial_data()
        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: пользователей — {users_count}, "
                f"проектов — {projects_count}."
            )
        )
