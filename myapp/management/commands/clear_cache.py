from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    '''
    Команда для отчистки кэша
    '''

    def handle(self, *args, **kwargs) -> None:
        cache.clear()
        self.stdout.write('Кэш очищен\n')