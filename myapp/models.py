from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
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

class MailingRegularity(models.Model):
    '''Модель переодичности рассылки'''
    name = models.CharField(max_length=50, verbose_name='Переодичность', unique=True)

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name = 'переодичность'
        verbose_name_plural = 'переодичности'


class MailingStatus(models.Model):
    '''Модель статуса рассылки'''
    name = models.CharField(max_length=50, verbose_name='Статус', unique=True)

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name = 'статус'
        verbose_name_plural = 'статусы'


class MailingSettings(models.Model):
    '''Модель рассылки'''
    owner = None
    title = models.CharField(max_length=80, verbose_name='Тема')
    body = models.TextField(verbose_name='Тело')
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, **NULLABLE)
    sending_time = models.DateTimeField(default=timezone.now, verbose_name='Время')
    regularity = models.ForeignKey(MailingRegularity, on_delete=models.SET_NULL, verbose_name='Периодичность',
                                   **NULLABLE)
    status = models.ForeignKey(MailingStatus, on_delete=models.CASCADE, verbose_name='Статус', **NULLABLE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь сервиса', **NULLABLE)

    def __str__(self) -> str:
        return f'{self.title}'

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'

    def get_active_mailing_count(self, status_name):
        return MailingSettings.objects.filter(status__name=status_name).count()


########################################################################
"""Модель логов рассылки"""

class MailingLog(models.Model):

    mailing = models.ForeignKey(MailingSettings, on_delete=models.CASCADE, verbose_name='Рассылка')
    attempt_datetime = models.DateTimeField(default=timezone.now, verbose_name='Последняя попытка')
    status = models.BooleanField(default=True, verbose_name='Статус попытки', **NULLABLE)
    server_response = models.TextField(verbose_name='Ответ сервера', default='OK')

    def __str__(self) -> str:
        return f'{self.mailing.title} - {self.status}'

    class Meta:
        verbose_name = 'лог рассылки'
        verbose_name_plural = 'логи рассылки'
