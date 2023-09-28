# Generated by Django 4.2.4 on 2023-09-25 17:21

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_alter_user_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.CharField(max_length=150, verbose_name='периодичность')),
                ('description', models.TextField(verbose_name='содержание')),
            ],
            options={
                'verbose_name': 'период',
                'verbose_name_plural': 'периоды',
            },
        ),
        migrations.AlterModelOptions(
            name='mailingsettings',
            options={'verbose_name': 'письмо', 'verbose_name_plural': 'письма'},
        ),
        migrations.RemoveField(
            model_name='client',
            name='user',
        ),
        migrations.RemoveField(
            model_name='mailinglog',
            name='last_attempt_datetime',
        ),
        migrations.RemoveField(
            model_name='mailinglog',
            name='last_attempt_response',
        ),
        migrations.RemoveField(
            model_name='mailinglog',
            name='last_attempt_status',
        ),
        migrations.RemoveField(
            model_name='mailinglog',
            name='mailing',
        ),
        migrations.RemoveField(
            model_name='mailinglog',
            name='response',
        ),
        migrations.RemoveField(
            model_name='mailinglog',
            name='send_datetime',
        ),
        migrations.RemoveField(
            model_name='mailinglog',
            name='status',
        ),
        migrations.RemoveField(
            model_name='mailinglog',
            name='timestamp',
        ),
        migrations.RemoveField(
            model_name='mailingsettings',
            name='completion_time',
        ),
        migrations.RemoveField(
            model_name='mailingsettings',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='mailingsettings',
            name='message',
        ),
        migrations.RemoveField(
            model_name='mailingsettings',
            name='send_time',
        ),
        migrations.AddField(
            model_name='mailingsettings',
            name='end_date',
            field=models.DateField(blank=True, null=True, verbose_name='окончание рассылки'),
        ),
        migrations.AddField(
            model_name='mailingsettings',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='начало рассылки'),
        ),
        migrations.AlterField(
            model_name='client',
            name='email',
            field=models.EmailField(max_length=150, unique=True, verbose_name='почта'),
        ),
        migrations.AlterField(
            model_name='mailingsettings',
            name='start_time',
            field=models.TimeField(default='12:00', verbose_name='время рассылки'),
        ),
        migrations.AlterField(
            model_name='mailingsettings',
            name='status',
            field=models.CharField(choices=[('created', 'Создана'), ('completed', 'Завершена'), ('started', 'Запущена')], default='создана', max_length=120, verbose_name='статус рассылки'),
        ),
        migrations.CreateModel(
            name='Logfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='дата и время последней попытки')),
                ('is_success', models.BooleanField(verbose_name='статус: успешно')),
                ('send_from', models.EmailField(max_length=254, verbose_name='от кого')),
                ('send_to', models.TextField(verbose_name='кому')),
                ('mail_title', models.CharField(max_length=150, verbose_name='тема письма')),
                ('mail_content', models.TextField(verbose_name='текст сообщения')),
                ('error', models.TextField(blank=True, null=True, verbose_name='текст ошибки')),
                ('mail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.mailingsettings', verbose_name='рассылка')),
            ],
            options={
                'verbose_name': 'лог',
                'verbose_name_plural': 'логи',
            },
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.client', verbose_name='клиент')),
                ('mail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.mailingsettings', verbose_name='письмо')),
            ],
        ),
        migrations.AddField(
            model_name='client',
            name='mails',
            field=models.ManyToManyField(through='myapp.Enrollment', to='myapp.mailingsettings'),
        ),
    ]
