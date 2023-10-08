import datetime
from django.db.models import Q
from myapp.models import MailingSettings, MailingStatus, MailingLog, Client


from myapp.services import send_email


def cron_send_email() -> None:
    now = datetime.datetime.now()
    mailings = MailingSettings.objects.filter(
        Q(status__name='создана') | Q(status__name='запущена')
    )

    for mailing in mailings:
        try:
            if mailing.sending_time <= now:
                clients_email_list = [str(client.email) for client in Client.objects.filter(user=mailing.user)]
                send_email(mailing.title, mailing.body, clients_email_list)
                MailingLog.objects.create(mailing=mailing)

                if mailing.regularity:
                    mailing.status = MailingStatus.objects.get(name='запущена')
                    if mailing.regularity.name == 'раз в день':
                        mailing.sending_time += datetime.timedelta(days=1)
                    elif mailing.regularity.name == 'раз в неделю':
                        mailing.sending_time += datetime.timedelta(weeks=1)
                    elif mailing.regularity.name == 'раз в месяц':
                        mailing.sending_time += datetime.timedelta(weeks=4)
                else:
                    mailing.status = MailingStatus.objects.get(name='завершена')

                mailing.save()

        except Exception as e:
            # Если произошла ошибка, создать запись в MailingLog с информацией об ошибке
            MailingLog.objects.create(mailing=mailing, status=False, server_response=str(e))

