from random import randint
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from myapp.models import User

import datetime
from myapp.tasks import send_newsletter, assign_running_status, assign_done_status
from myapp.funcs import revert_command
from background_task.models import Task


def create_mailing(obj):
    hour = obj.sending_time.hour - 3
    start = datetime.datetime(year=obj.start_date.year, month=obj.start_date.month, day=obj.start_date.day,
                              hour=hour, minute=obj.sending_time.minute,
                              second=obj.sending_time.second)
    end = datetime.datetime(year=obj.end_date.year, month=obj.end_date.month, day=obj.end_date.day,
                            hour=hour, minute=obj.sending_time.minute,
                            second=obj.sending_time.second)
    rep = revert_command(obj.sending_period.description)

    send_newsletter(obj.pk, schedule=start, repeat=rep, repeat_until=end)
    assign_running_status(obj.pk, schedule=start)
    assign_done_status(obj.pk, schedule=end)


def resume_mailing(mail):
    hour = mail.sending_time.hour - 3
    start = datetime.datetime(year=mail.start_date.year, month=mail.start_date.month, day=mail.start_date.day,
                              hour=hour, minute=mail.sending_time.minute,
                              second=mail.sending_time.second)
    end = datetime.datetime(year=mail.end_date.year, month=mail.end_date.month, day=mail.end_date.day,
                            hour=hour, minute=mail.sending_time.minute,
                            second=mail.sending_time.second)
    rep = revert_command(mail.sending_period.description)

    send_newsletter(mail.pk, schedule=start, repeat=rep, repeat_until=end)
    assign_done_status(mail.pk, schedule=end)


def delete_status_task(mail):
    status_tasks = Task.objects.filter(task_name='mailing.tasks.assign_done_status')
    for task in status_tasks:
        params = task.params
        params = params()[0][0]
        if params == mail.pk:
            mail_status_task = task
            mail_status_task.delete()


def delete_sending_task(mail):
    send_tasks = Task.objects.filter(task_name='mailing.tasks.send_newsletter')
    for task in send_tasks:
        params = task.params
        params = params()[0][0]
        if params == mail.pk:
            mail_status_task = task
            mail_status_task.delete()

def add_group(user):
    group = Group.objects.get(name='Service_user')
    user.groups.add(group)
    user.save()


def send_registration_mail(user):
    user.is_active = False
    user.save()
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_url = reverse_lazy('users:confirm_email', kwargs={'uidb64': uid, 'token': token})
    current_site = settings.SITE_NAME
    send_mail(
        subject='Регистрация на сайте',
        message=f'Вы зарегистрировались на нашей платформе, пожалуйста подтвердите свой email: '
                f'http://{current_site}{activation_url}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email]
    )


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
