from django.core.management import BaseCommand
from myapp.models import Period


class Command(BaseCommand):

    def handle(self, *args, **options):
        Period.objects.all().delete()
        Period.objects.create(period="раз в час", description="hour")
        Period.objects.create(period="раз в день", description="day")
        Period.objects.create(period="раз в неделю", description="week")
        Period.objects.create(period="раз в месяц", description="month")
        Period.objects.create(period="никогда", description="never")
