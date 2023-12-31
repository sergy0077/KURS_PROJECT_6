# Generated by Django 4.2.4 on 2023-09-21 10:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300, verbose_name='название')),
                ('content', models.TextField(verbose_name='содержание')),
                ('preview', models.ImageField(blank=True, null=True, upload_to='articles/', verbose_name='изображение')),
                ('image', models.ImageField(upload_to='blog_images/')),
                ('creation_date', models.DateField(default=django.utils.timezone.now, verbose_name='дата публикации')),
                ('views_count', models.IntegerField(default=0, verbose_name='количество просмотров')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'статья',
                'verbose_name_plural': 'статьи',
            },
        ),
    ]
