
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from myapp.models import MailingSettings
from myapp.views import CreateMailing
import sys

# Создаем планировщик
scheduler = BackgroundScheduler()

# Функция, которую мы хотим запускать периодически
def my_scheduled_job():
    # Создаем экземпляр формы CreateMailing и вызываем метод form_valid
    form = CreateMailing()
    form.setup(form.request)  # Необходимо правильно настроить форму, возможно, путем передачи запроса
    if form.is_valid():
        form.form_valid(form.form)  # Вызываем метод form_valid с переданной формой
    else:
        print("Invalid form data")  # Обрабатываем неверные данные формы

# Функция для запуска планировщика
def start_scheduler():
    try:
        if MailingSettings.status:
            if MailingSettings.PERIODS == 'PERIOD_HOURLY':
                scheduler.add_job(my_scheduled_job, 'interval', hours=1,  name='send_mailings', id='hourly_job')
            elif MailingSettings.PERIODS == 'PERIOD_DAILY':
                scheduler.add_job(my_scheduled_job, 'interval', hours=24, name='send_mailings', id='daily_job')
            elif MailingSettings.PERIODS == 'PERIOD_WEEKLY':
                scheduler.add_job(my_scheduled_job, 'interval', hours=168, name='send_mailings', id='weekly_job')
            scheduler.start()
            print("Scheduler started...", file=sys.stdout)
        else:
            scheduler.pause()
            print("Scheduler paused...", file=sys.stdout)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

# Функция для остановки задачи по ее имени
def stop_scheduler_job(job_id):
    try:
        scheduler.remove_job(job_id)
        print(f"Job '{job_id}' removed successfully")
    except JobLookupError:
        print(f"Job '{job_id}' not found")

# Функция для остановки всех задач
def stop_all_scheduler_jobs():
    try:
        scheduler.remove_all_jobs()
        print("All jobs removed successfully")
    except JobLookupError:
        print("No jobs found")

# Проверяем, если скрипт запущен напрямую (а не импортирован как модуль), то запускаем планировщик
if __name__ == "__main__":
    start_scheduler()
