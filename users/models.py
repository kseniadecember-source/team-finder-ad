import random
import uuid
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont


class UserManager(BaseUserManager):
    """Менеджер для кастомной модели User с email вместо username."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


def random_color():
    """Возвращает случайный умеренно насыщенный цвет для фона аватара."""
    r = random.randint(50, 150)
    g = random.randint(50, 150)
    b = random.randint(50, 150)
    return (r, g, b)


def _load_avatar_font(size=110):
    """Загружает шрифт для генерации аватара с запасными вариантами."""
    font_candidates = [
        Path(settings.BASE_DIR)
        / "static"
        / "fonts"
        / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf",
        "arial.ttf",
        "DejaVuSans-Bold.ttf",
    ]
    for candidate in font_candidates:
        try:
            return ImageFont.truetype(str(candidate), size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def generate_avatar(name):
    """Генерирует аватар с первой буквой имени на однотонном фоне."""
    size = 200
    bg_color = random_color()
    text_color = (255, 255, 255)
    image = Image.new("RGB", (size, size), bg_color)
    draw = ImageDraw.Draw(image)
    letter = (name.strip()[0] if name and name.strip() else "?").upper()
    font = _load_avatar_font(size=110)
    bbox = draw.textbbox((0, 0), letter, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(
        ((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]),
        letter,
        fill=text_color,
        font=font,
    )
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"avatar_{uuid.uuid4().hex}.png")


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=124, verbose_name="Имя")
    surname = models.CharField(max_length=124, verbose_name="Фамилия")
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        verbose_name="Аватар",
    )
    phone = models.CharField(
        max_length=12,
        blank=True,
        default="",
        verbose_name="Телефон",
    )
    github_url = models.URLField(blank=True, verbose_name="GitHub")
    about = models.TextField(max_length=256, blank=True, verbose_name="О себе")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Администратор")
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name="Избранные проекты",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ("-id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.surname} {self.name}"

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = generate_avatar(self.name)
        super().save(*args, **kwargs)
