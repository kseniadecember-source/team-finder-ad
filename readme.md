# TeamFinder — платформа для поиска команды на Pet-проекты (Вариант 1)

**TeamFinder** — веб-приложение на Django и PostgreSQL, позволяющее разработчикам, дизайнерам и другим специалистам публиковать идеи Pet-проектов, находить единомышленников, откликаться на проекты и формировать список избранных проектов.

Реализован **Вариант 1**:
- Добавление и удаление проектов в «Избранное» (с главной страницы, со страницы проекта и со страницы избранного).
- Отдельная страница «Избранное» (`/projects/favorites/`).
- Фильтрация пользователей на странице `/users/list/` по 4 критериям:
  - «Авторы избранных проектов» (`?filter=owners-of-favorite-projects`)
  - «Авторы проектов, в которых я участвую» (`?filter=owners-of-participating-projects`)
  - «Пользователи, которым нравятся мои проекты» (`?filter=interested-in-my-projects`)
  - «Участники моих проектов» (`?filter=participants-of-my-projects`)

---

## Инструкция для ревьюера по запуску проекта

### 1. Клонирование репозитория и настройка виртуального окружения

```bash
git clone https://github.com/kseniadecember-source/team-finder-ad.git
cd team-finder-ad
python -m venv venv
```

Активируйте виртуальное окружение:
- **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```
- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```

Установите зависимости:

```bash
pip install -r requirements.txt
```

---

### 2. Настройка переменных окружения (`.env`)

Скопируйте пример конфигурационного файла `.env_example` в `.env`:

```bash
cp .env_example .env
```

По умолчанию в `.env_example` уже заданы рабочие параметры для локального запуска с Docker Compose (`TASK_VERSION=1`, порт PostgreSQL `5432`):

| Переменная            | Значение по умолчанию | Описание                                                |
|-----------------------|-----------------------|---------------------------------------------------------|
| `DJANGO_SECRET_KEY`   | `django-insecure-...` | Секретный ключ Django                                   |
| `DJANGO_DEBUG`        | `True`                | Режим отладки (`True` / `False`)                        |
| `POSTGRES_DB`         | `team_finder`         | Имя базы данных PostgreSQL                              |
| `POSTGRES_USER`       | `team_finder`         | Пользователь PostgreSQL                                 |
| `POSTGRES_PASSWORD`   | `team_finder`         | Пароль пользователя PostgreSQL                          |
| `POSTGRES_HOST`       | `localhost`           | Хост БД (`localhost`)                                   |
| `POSTGRES_PORT`       | `5432`                | Порт подключения к PostgreSQL                           |
| `TASK_VERSION`        | `1`                   | Номер варианта задания (`1` — использует `templates_var1`) |

---

### 3. Запуск PostgreSQL через Docker Compose

В корне проекта расположен `docker-compose.yml` с настроенным томом (`volumes: postgres_data`) для сохранения данных между перезапусками контейнера:

```bash
docker compose up -d
```

---

### 4. Применение миграций и тестовые данные

Выполните миграции базы данных:

```bash
python manage.py migrate
```

> **Примечание:** При первом выполнении `python manage.py migrate` автоматически запускается миграция начальных данных (`0002_seed_initial_data`), которая создаёт **5 тестовых пользователей** (включая администратора), генерирует им аватарки и создаёт проекты, связи участия и избранного.
> При необходимости вы также можете повторно вызвать команду наполнения вручную:
> ```bash
> python manage.py seed_data
> ```

#### Учётные данные тестовых пользователей

| Роль          | Email                   | Пароль              | Имя и фамилия       |
|---------------|-------------------------|---------------------|---------------------|
| Администратор | `admin@teamfinder.ru`   | `AdminPassword123!` | Ксения Декабрьская  |
| Пользователь  | `alexey@teamfinder.ru`  | `UserPassword123!`  | Алексей Смирнов     |
| Пользователь  | `maria@teamfinder.ru`   | `UserPassword123!`  | Мария Соколова      |
| Пользователь  | `dmitry@teamfinder.ru`  | `UserPassword123!`  | Дмитрий Волков      |
| Пользователь  | `elena@teamfinder.ru`   | `UserPassword123!`  | Елена Морозова      |

---

### 5. Запуск сервера разработки

```bash
python manage.py runserver
```

После запуска веб-приложение доступно по адресу:
- **Приложение:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Админ-панель:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

### 6. Запуск тестов и проверка стиля кода (PEP 8)

```bash
python manage.py test
flake8
```
