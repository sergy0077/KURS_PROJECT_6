from random import randint
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from myapp.models import User
from blog.models import BlogPost
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import QuerySet
from myapp.models import MailingStatus, MailingSettings


def send_email(title: str, body: str, users_email_list: list[User]) -> None:
    '''Функция отправляет e-mail сообщение на указанную почту/ы
    :param title: имя сообщения
    :param body: тело сообщения
    :param users_email_list: список e-mail адресов получателей'''
    try:
        send_mail(
            title,
            body,
            settings.EMAIL_HOST_USER,
            users_email_list,
            fail_silently=False
        )
    except Exception as e:
        print(
            'Ошибка отправки\n'
            f'Ошибка: {e}'
        )


def check_user(user: User, current_user: User) -> bool:
    '''Функция проверяет, что пользователь объекта является
    текущим, чтобы видеть страницу объекта, иначе переходит на другую
    страницу
    :param user: пользователь объекта
    :param current_user: текущий пользователь
    :return: bool'''
    return user == current_user


def get_status_object(status_name: str) -> MailingStatus:
    '''Функция возвращает объект класса MailingStatus по переданному имени
    :param status_name: имя статуса
    :return: MailingStatus objects'''
    try:
        status = MailingStatus.objects.get(name=status_name)
        return status
    except Exception as e:
        print(f'Ошибка - {e}')


def check_mailing_status(mailing: MailingSettings, status_name: str) -> bool:
    '''Функция проверят, что статус рассылки равен переданому
    :param mailing: рассылка сервиса
    :param status_name: имя статуса
    :return: bool'''
    status = get_status_object(status_name)

    return mailing.status == status


def get_articles_from_cache() -> QuerySet:
    '''Функция возвращает все статьи из кэша. Если кэш пуст,
    то сохраняет статьи из базы данных в него
    :return: QuerySet состоящий из объектов Article'''
    if settings.CACHE_ENABLED:
        key = 'articles'
        cached_data = cache.get(key)

        if cached_data is None:
            cached_data = BlogPost.objects.all()
            cache.set(key, cached_data, 600)

        return cached_data

    return BlogPost.objects.all()

#####################################################################################
'''Функции авторизации'''

def check_link(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        is_success = True

    else:
        is_success = False
    return is_success


def send_reset_password_mail(email):
    user = User.objects.get(email=email)
    new_password = "".join([str(randint(0, 9)) for _ in range(12)])
    send_mail(
        subject='Смена пароля',
        message=f'Ваш новый пароль: {new_password}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email]
    )
    user.set_password(new_password)
    user.save()


def send_block_notification(user):
    send_mail(
        subject='Блокировка аккаунта',
        message=f'Ваш аккаунт был заблокирован. Пожалуйста обратитесь к менеджеру за подробностями.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email]
    )
