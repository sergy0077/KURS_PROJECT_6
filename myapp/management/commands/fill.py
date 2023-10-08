from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    '''
    Комманда для заполнения данными базу данных
    '''

    def handle(self, *args, **options) -> None:
        try:
            call_command('loaddata', 'database_data.json')
        except:
            self.stderr.write('Ошибка загрузки данных!')
