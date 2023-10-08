from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand
from django.db.models import Q
from django.utils import timezone

from cron import cron_send_email
from myapp.models import MailingSettings
from myapp.services import get_status_object
from myapp.models import User


class Command(BaseCommand):
    '''Команда для отправки рассылок пользователей'''

    def handle(self, *args, **options) -> None:
        try:
            user = self.__get_user()
            mailing = self.__get_mailings(user)

            self.__send_email(mailing)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist('Пользователя или рассылок не существует!')
        except KeyboardInterrupt:
            self.stdout.write('\nВсего доброго!')
            quit()

    def __get_user(self) -> User:
        '''
        Возвращает выбраного пользователя сервиса
        :return: User
        '''
        users = User.objects.exclude(is_staff=True)
        users_dict = {num: user for num, user in enumerate(users, start=1)}

        self.stdout.write('Пользователи:')

        for num, user in users_dict.items():
            self.stdout.write(f'{num} - {user.email}')

        while True:
            if not users_dict:
                self.stderr.write('Пользователей не найдено')
                raise KeyboardInterrupt
            try:
                user_input = int(input('Для выбора пользователя укажите его номер: '))
                user = users_dict[user_input]
                break
            except ValueError:
                self.stderr.write('Вы ввели не число!')
            except KeyError:
                self.stderr.write('Такого пользователя не существует')

        return user

    def __get_mailings(self, user: User) -> MailingSettings:
        '''Возвращает выбранную рассылку пользователя сервиса
        :param user: пользователь сервиса
        :return: list[Mailing]'''
        mailings = MailingSettings.objects.filter(Q(user=user) & ~Q(status=get_status_object('завершена')))
        mailing_dict = {num: mailing for num, mailing in enumerate(mailings, start=1)}

        self.stdout.write('Рассылки:')

        for num, mailing in mailing_dict.items():
            sending_time = mailing.sending_time.astimezone(timezone.get_current_timezone()).strftime(
                '%d-%m-%Y %H:%M:%S'
            )
            self.stdout.write(f'{num} - {mailing.title} ({sending_time})')

        while True:
            if not mailing_dict:
                self.stderr.write('Рассылок не найдено!')
                raise KeyboardInterrupt
            try:
                user_input = int(input('Для выбора рассылки, которую необходимо '
                                       'отправить прямо сейчас, укажите её номер: '))
                mailing = mailing_dict[user_input]
                break
            except ValueError:
                self.stderr.write('Вы ввели не число!')
            except KeyError:
                self.stderr.write('Такой рассылки не существует')

        return mailing

    def __send_email(self, mailing: MailingSettings) -> None:
        '''Отправляет выбранную рассылку прямо сейчас
        :param mailing:'''
        mailing.sending_time = timezone.now()
        mailing.save()
        cron_send_email()