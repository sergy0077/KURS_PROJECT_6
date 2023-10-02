import os
import django

# Устанавливаем переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # Замените "config.settings" на путь к вашему файлу settings.py

# Инициализируем Django
django.setup()

# Теперь вы можете импортировать и запустить ваш cron.py
import cron

cron.start_scheduler()
