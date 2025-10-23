# Сервис управления рассылками

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)

Сервис для управления email-рассылками с возможностью автоматической отправки, статистикой и разграничением прав доступа.

## Возможности

- 📧 Создание и управление рассылками
- 📊 Подробная статистика отправок
- ⏰ Автоматическая отправка по расписанию
- 🔐 Разграничение прав (пользователи и менеджеры)
- 🚀 Высокая производительность благодаря кешированию
- 📝 Логирование всех операций

## Установка и ЗАПУСК ПРОЕКТА

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/mailing_service.git
   ```
   ```bash
   cd mailing_service
   ```
    Создайте и активируйте виртуальное окружение:

    ```bash
    python -m venv venv
    ```
    ```bash
    source venv/bin/activate
    ```
    Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```
    Настройте переменные окружения:
    ```bash
    cp .env.example .env
    ```
    Примените миграции:   
    ```bash
    python manage.py migrate
    ```
    Запустите сервер:   
    ```bash
    python manage.py runserver
    ```


## Структура проекта
```
mailing_service/
├── config/               # Основные настройки проекта
├── mailing/              # Приложение рассылок
│   ├── management/       # Пользовательские команды
│   ├── migrations/       # Миграции базы данных
│   ├── templates/        # Шаблоны
│   ├── models.py         # Модели данных
│   ├── views.py          # Представления
│   └── ...
├── users/                # Приложение пользователей
├── static/               # Статические файлы
├── templates/            # Базовые шаблоны
├── .env                  # Переменные окружения
├── .gitignore            # Игнорируемые файлы
├── manage.py             # Управление Django
└── README.md             # Этот файл
```
## Использование:
```bash
    Зарегистрируйтесь или войдите в систему

    Создайте клиентов для рассылки

    Создайте шаблоны сообщений

    Настройте рассылку с указанием времени и получателей

    Просматривайте статистику в личном кабинете

    Для менеджеров доступны:

    Просмотр всех рассылок

    Отключение рассылок

    Управление пользователями
```

## Лицензия
MIT License