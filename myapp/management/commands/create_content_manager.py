from django.core.management import BaseCommand
from django.contrib.auth.models import Group
from myapp.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        email_adress = input("email ")
        f_name = input("username ")
        l_name = input("fullname ")
        password = input("password ")

        user = User.objects.create(
            email=email_adress,
            username=f_name,
            fullname=l_name,
            is_staff=True,
            is_active=True
        )

        user.set_password(password)
        user.save()

        content_manager = Group.objects.get(name='Content_manager')
        content_manager.user_set.add(user)
