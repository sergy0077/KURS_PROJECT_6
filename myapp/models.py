from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from config import settings


NULLABLE = {'blank': True, 'null': True}

##########################################################################
"""Модель Пользователя - USER"""

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=150, verbose_name='имя пользователя', unique=True, null=True)
    email = models.EmailField(max_length=150, verbose_name='почта', unique=True)
    phone = models.CharField(max_length=35, verbose_name='номер телефона', **NULLABLE)
    fullname = models.CharField(max_length=150, verbose_name='ФИ0')
    comment = models.TextField(verbose_name='комментарий', **NULLABLE)
    avatar = models.ImageField(upload_to='user/', verbose_name='фото', null=True, blank=True)
    is_manager = models.BooleanField(default=False,  verbose_name='activity')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username or self.email or "User"


###########################################################################
"""Модель для клиента сервися рассылок"""

class Client(models.Model):
    DoesNotExist = None
    objects = None
    full_name = models.CharField(max_length=150, verbose_name='ФИО', **NULLABLE)
    email = models.EmailField(max_length=150, unique=True, verbose_name='почта')
    comment = models.TextField(verbose_name='комментарий', **NULLABLE)

    # Зависимость от владельца клиента
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='владелец_клиента', **NULLABLE)
    mails = models.ManyToManyField('myapp.MailingSettings', through="Enrollment")

    objects = models.Manager()

    def __str__(self):
        return f'{self.full_name}, {self.email}'

    class Meta:
        """Представление написания заголовков для клиента в админке"""
        verbose_name = "клиент"
        verbose_name_plural = "клиенты"


class Enrollment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='клиент')
    mail = models.ForeignKey('myapp.MailingSettings', on_delete=models.CASCADE, verbose_name='письмо')


##########################################################################
"""Модель Сообщения для рассылки"""

class Message(models.Model):
    objects = None
    subject = models.CharField (max_length=180, verbose_name='тема письма')
    body = models.TextField (verbose_name='сообщение')
    content = models.TextField()

    # Зависимость от владельца сообщения
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models. SET_NULL, verbose_name='владелец сообщения', **NULLABLE)

    def __str_(self):
        return f'{self.subject}, {self.body}'

    class Meta:
        """Представление налисания заголовков для письма в админке"""
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"


#############################################################################################
"""Модель рассылки"""

class Period(models.Model):
    period = models.CharField(max_length=150, verbose_name='периодичность')
    description = models.TextField(verbose_name='содержание')

    def __str__(self):
        return f'{self.period}'

    class Meta:
        verbose_name = 'период'
        verbose_name_plural = 'периоды'


class MailingSettings(models.Model):
    objects = None
    # FREQUENCY_CHOICE = (
    #     ("daily", "ежедневно"),
    #     ("weekly", "еженедельно"),
    #     ("monthly", "ежемесячно"),
    # )
    #
    STATUS_CHOICE = (
    ("created", "Создана"),
    ("completed", "Завершена"),
    ("started", "Запущена"),
    )
    PERIOD_HOURLY = 'hourly'
    PERIOD_DAILY = 'daily'
    PERIOD_WEEKLY = 'weekly'

    PERIODS = (
        (PERIOD_HOURLY, 'Раз в час'),
        (PERIOD_DAILY, 'Ежедневная'),
        (PERIOD_WEEKLY, 'Раз в неделю'),
    )
    title = models.CharField(max_length=25, verbose_name='Название рассылки')
    theme_mess = models.CharField(max_length=200, verbose_name='Тема письма')
    body_mess = models.TextField(verbose_name='Тело письма')

    start_time = models.TimeField(auto_now_add=False, default='12:00', verbose_name='время рассылки')
    frequency = models.CharField(max_length=30, choices=PERIODS, default='daily', verbose_name='периодичность рассылки')
    start_date = models.DateField(default=now, verbose_name='начало рассылки')
    end_date = models.DateField(**NULLABLE, verbose_name='окончание рассылки')
    status = models.CharField(max_length=120, choices=STATUS_CHOICE, default='создана', verbose_name='статус рассылки')
    is_active = models.BooleanField(default=True, verbose_name='статус активности')

    clients = models.ManyToManyField(Client, verbose_name='клиенты')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='владелец рассылки', **NULLABLE)

    objects = models.Manager()

    def _str__(self):
        return (f"Рассылка #{self.pk}. Время отправки - {self.send_time} "
                f"Периодичность - {self. frequency}. Статутс {self.status}"
                f"Название рассылки {self.title}")

    class Meta:
        verbose_name = 'письмо'
        verbose_name_plural = 'письма'


########################################################################
"""Модель логов рассылки"""

class MailingLog(models.Model):
    objects = None
    STATUS_ATTEMPTED = 'attempted'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = (
        (STATUS_ATTEMPTED, 'Attempted'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
    )

    mailing = models.ForeignKey(MailingSettings, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    send_datetime = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ATTEMPTED)
    response = models.TextField(default='No response received yet')
    last_attempt_datetime = models.DateTimeField(null=True, blank=True)
    last_attempt_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ATTEMPTED)
    error_msg = models.TextField(verbose_name='Ответ сервера', **NULLABLE)

    objects = models.Manager()

    def __str__(self):
        return f'{self.status} {self.client} {self.mailing} {self.error_msg}'


class Logfile(models.Model):
    date = models.DateTimeField(verbose_name='дата и время последней попытки')
    is_success = models.BooleanField(verbose_name='статус: успешно')
    mail = models.ForeignKey(MailingSettings, on_delete=models.CASCADE, verbose_name='рассылка')
    send_from = models.EmailField(verbose_name='от кого')
    send_to = models.TextField(verbose_name='кому')
    mail_title = models.CharField(max_length=150, verbose_name='тема письма')
    mail_content = models.TextField(verbose_name='текст сообщения')
    error = models.TextField(** NULLABLE, verbose_name='текст ошибки')

    objects = models.Manager()

    def __str__(self):
        return f'Лог {self.pk}'

    class Meta:
        verbose_name = 'лог'
        verbose_name_plural = 'логи'