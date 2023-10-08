import os
import django

# Устанавливаем переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Инициализируем Django
django.setup()

# Импортируем и запускаем cron.py
import cron

cron.cron_send_email()
