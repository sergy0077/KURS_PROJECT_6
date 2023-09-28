from datetime import timezone
import requests
from .models import MailingLog, MailingSettings, Client
from threading import current_thread
from django.utils.deprecation import MiddlewareMixin

def send_mailing_task(mailing_id, client_id, mailing_settings=None):
    try:
        # код отправки рассылки
        message_data = {
            "recipient": "recipient@example.com",
            "subject": "Hello from My Service",
            "content": "This is a test email from My Service.",
        }
        response = requests.post('http://api.myservice.com/send_message/', data=message_data)

        # Обновляем запись в логах с информацией об отправке
        mailing_log = MailingLog.objects.get(mailing_id=mailing_id, client_id=client_id)
        mailing = MailingSettings.objects.get(pk=mailing_id)
        client = Client.objects.get(pk=client_id)

        # Создание или обновление записи в логах рассылки
        mailing_log.status = MailingLog.STATUS_ATTEMPTED
        mailing_log.last_attempt_datetime = timezone.now()
        mailing_log.last_attempt_status = MailingLog.STATUS_ATTEMPTED
        mailing_log.response = 'No response received yet'
        mailing_log.save()

        # Обработка успешной отправки
        if response.status_code == 200:  # Проверка на успешный ответ от внешнего сервиса
            mailing_log.status = MailingLog.STATUS_SUCCESS
        else:
            mailing_log.status = MailingLog.STATUS_FAILED

        mailing_log.response = response.text
        mailing_log.last_attempt_status = mailing_log.status
        mailing_log.last_attempt_response = response.text
        mailing_log.save()

    except MailingSettings.DoesNotExist:
        # Обработка, если настройки рассылки не найдены
        create_failed_log(client, 'Mailing settings not found')
    except Client.DoesNotExist:
        # Обработка, если клиент не найден
        create_failed_log(client, 'Client not found')
    except requests.RequestException as e:
        # Обработка ошибок связанных с запросом
        create_failed_log(client, str(e))
    except Exception as e:
        # Обработка других исключений
        create_failed_log(client, 'An error occurred: ' + str(e))


def create_failed_log(client, response):
    mailing_log = MailingLog.objects.create(
        client=client,
        status=MailingLog.STATUS_FAILED,
        last_attempt_datetime=timezone.now(),
        last_attempt_status=MailingLog.STATUS_FAILED,
        response=response,
    )
    return mailing_log


_requests = {}


def get_current_request():
    t = current_thread()
    if t not in _requests:
        return None
    return _requests[t]


class RequestMiddleware(MiddlewareMixin):

    def process_request(self, request):
        _requests[current_thread()] = request


