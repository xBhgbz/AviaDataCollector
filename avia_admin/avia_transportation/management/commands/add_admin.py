import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Создать администратора на основе переменных окружения"

    def handle(self, *args, **kwargs):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")

        if not username or not password or not email:
            self.stdout.write(
                self.style.ERROR(
                    "Переменные окружения "
                    "DJANGO_SUPERUSER_USERNAME, "
                    "DJANGO_SUPERUSER_PASSWORD "
                    "и DJANGO_SUPERUSER_USERNAME "
                    "должны быть установлены."
                )
            )
            return

        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if not user:
            User.objects.create_superuser(
                username=username, password=password, email=email
            )
            self.stdout.write(
                self.style.SUCCESS(f"Суперпользователь {username} успешно создан.")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Пользователь с именем {username} уже существует.")
            )