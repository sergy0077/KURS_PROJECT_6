# Generated by Django 4.2.4 on 2023-09-20 12:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_user_username'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BlogPost',
        ),
    ]
