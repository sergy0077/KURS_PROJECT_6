from datetime import datetime
from background_task import background
from django.conf import settings
from django.core.mail import send_mail
from django_cron import CronJobBase, Schedule
from django.utils import timezone
from .models import MailingSettings, MailingLog, Logfile
from .utils import send_mailing_task
from celery import shared_task
from django.core.mail import send_mail
from myapp.models import MailingSettings, Logfile


class ProcessMailings(CronJobBase):
    RUN_AT_TIMES = ['00:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'myapp.process_mailings'

    def do(self):
        current_time = timezone.now()
        active_mailings = MailingSettings.objects.filter(start_time__lte=current_time, end_time__gt=current_time)

        for mailing in active_mailings:
            clients = mailing.clients.all()  # Получаем все клиенты связанные с рассылкой
            for client in clients:
                # Отправляем рассылку для каждого клиента
                send_mailing_task.delay(mailing.id, client.id)
                # Создаем запись в логах
                MailingLog.objects.create(mailing=mailing, client=client, last_attempt_datetime=current_time,
                                          last_attempt_status='attempted')

@shared_task
def send_newsletter(mail_id):
    is_suc = True
    error = 'No errors'
    clients_list = []
    mail_item = MailingSettings.objects.get(pk=mail_id)
    for client in mail_item.clients.all():
        clients_list.append(client.email)
    print(clients_list)
    print(mail_item)
    try:
        send_mail(
            mail_item.title,
            mail_item.content,
            settings.EMAIL_HOST_USER,
            clients_list,
            fail_silently=False
        )
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        is_suc = False
        error = f"Unexpected {err=}, {type(err)=}"
    finally:
        send_at = datetime.now()
        log = Logfile.objects.create(date=send_at, is_success=is_suc, mail=mail_item,
                                     send_from=settings.EMAIL_HOST_USER, send_to=', '.join(clients_list),
                                     mail_title=mail_item.title, mail_content=mail_item.content, error=error)
        log.save()



@background
def assign_running_status(mail_id):
    mail_item = MailingSettings.objects.get(pk=mail_id)
    mail_item.status = 'запущена'
    mail_item.save()


@background
def assign_done_status(mail_id):
    mail_item = MailingSettings.objects.get(pk=mail_id)
    mail_item.status = 'завершена'
    mail_item.save()