from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):

    def handle(self, *args, **options):
        manager = Group.objects.create(name='Manager')
        content_manager = Group.objects.create(name='Content_manager')
        service_user = Group.objects.create(name='Service_user')

        add_mail = Permission.objects.get(codename='add_mail')
        change_mail = Permission.objects.get(codename='change_mail')
        view_mail = Permission.objects.get(codename='view_mail')
        delete_mail = Permission.objects.get(codename='delete_mail')
        add_article = Permission.objects.get(codename='add_article')
        change_article = Permission.objects.get(codename='change_article')
        delete_article = Permission.objects.get(codename='delete_article')
        view_article = Permission.objects.get(codename='view_article')
        add_client = Permission.objects.get(codename='add_client')
        change_client = Permission.objects.get(codename='change_client')
        view_client = Permission.objects.get(codename='view_client')
        delete_client = Permission.objects.get(codename='delete_client')
        delete_task = Permission.objects.get(codename='delete_task')
        view_user = Permission.objects.get(codename='view_user')
        set_active = Permission.objects.get(codename='set_active')

        manager_perm_list = [view_mail, view_client, view_article, view_user, set_active, delete_task]
        content_manager_perm_list = [add_article, change_article, view_article, delete_article, view_mail]
        service_user_perm_list = [add_mail, change_mail, view_mail, delete_mail, add_client,
                                  change_client, view_client, delete_client, view_article, delete_task]

        manager.permissions.set(manager_perm_list)
        content_manager.permissions.set(content_manager_perm_list)
        service_user.permissions.set(service_user_perm_list)
