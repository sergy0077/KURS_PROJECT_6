from celery import Celery, shared_task
from django.utils import timezone
from django.core.mail import send_mail
from myapp.models import MailingSettings, MailingLog

app = Celery('myapp')


@shared_task
def send_mailing(mailing_id):
    try:
        mailing = MailingSettings.objects.get(id=mailing_id)
        if mailing.start_time <= timezone.now().time():
            for client in mailing.clients.all():
                try:
                    send_mail(
                        subject=mailing.message.subject,
                        message=mailing.message.body,
                        from_email='your@email.com',
                        recipient_list=[client.email],
                    )
                    status = 'success'
                    response = 'Email sent successfully'
                except Exception as e:
                    status = 'error'
                    response = str(e)
                MailingLog.objects.create(
                    send_datetime=timezone.now(),
                    status=status,
                    response=response,
                    mailing=mailing,
                )
    except MailingSettings.DoesNotExist:
        pass
