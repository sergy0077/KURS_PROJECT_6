from django.db import models
from django.urls import reverse
from django.utils.timezone import now

NULLABLE = {'blank': True, 'null': True}


class BlogPost(models.Model):

    """Модель для записей блога"""

    objects = None
    title = models.CharField(max_length=300, verbose_name='название')
    content = models.TextField(verbose_name='содержание')
    preview = models.ImageField(upload_to='articles/', verbose_name='изображение', null=True, blank=True)
    #image = models.ImageField(upload_to='blog_images/', verbose_name='изображение')
    creation_date = models.DateField(default=now, verbose_name='дата публикации')
    views_count = models.IntegerField(default=0, verbose_name='количество просмотров')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'статья'
        verbose_name_plural = 'статьи'

