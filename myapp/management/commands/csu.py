from django.core.management import BaseCommand
from myapp.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email='sky_pro2023@mail.ru',
            first_name='Admin',
            last_name='Sky_Pro',
            is_staff=True,
            is_superuser=True
        )

        user.set_password('9MoXf1JU4RBp')
        user.save()