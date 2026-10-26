from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from projects.models import Project

User = get_user_model()

TEST_USERS = [
    {
        "email": "admin@teamfinder.ru",
        "password": "AdminPassword123!",
        "name": "Ксения",
        "surname": "Войтышена",
        "phone": "+79990000001",
        "github_url": "https://github.com/kseniadecember-source",
        "about": "Администратор сайта.",
        "is_staff": True,
        "is_superuser": True,
        "projects": [
            {
                "name": "TeamFinder",
                "description": "Сайт для поиска команды на pet-проекты.",
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
        "github_url": "",
        "about": "Пишу бэкенд на Python и Django.",
        "is_staff": False,
        "is_superuser": False,
        "projects": [
            {
                "name": "Трекер задач для группы",
                "description": (
                    "Простой трекер задач с дедлайнами для учебной группы."
                ),
                "github_url": "",
                "status": Project.STATUS_OPEN,
            },
            {
                "name": "Бот-напоминалка",
                "description": "Telegram-бот, который напоминает о дедлайнах.",
                "github_url": "",
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
        "github_url": "",
        "about": "Верстаю и пишу фронтенд на React.",
        "is_staff": False,
        "is_superuser": False,
        "projects": [
            {
                "name": "Сайт-портфолио",
                "description": (
                    "Шаблон сайта-портфолио для начинающих дизайнеров."
                ),
                "github_url": "",
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
        "github_url": "",
        "about": "Изучаю анализ данных, много работаю с SQL.",
        "is_staff": False,
        "is_superuser": False,
        "projects": [
            {
                "name": "Погода в графиках",
                "description": (
                    "Собираем данные о погоде и строим графики по месяцам."
                ),
                "github_url": "",
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
        "github_url": "",
        "about": "Тестировщик, пишу автотесты на pytest.",
        "is_staff": False,
        "is_superuser": False,
        "projects": [
            {
                "name": "Автотесты для учебного магазина",
                "description": (
                    "Проверяем корзину и оформление заказа в учебном магазине."
                ),
                "github_url": "",
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
                f"Пользователей: {users_count}, проектов: {projects_count}."
            )
        )
