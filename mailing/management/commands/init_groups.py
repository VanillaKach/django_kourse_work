from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing.models import Mailing, Message, Client


class Command(BaseCommand):
    help = 'Creates initial groups and permissions'

    def handle(self, *args, **options):
        # Создаем группу менеджеров
        managers_group, created = Group.objects.get_or_create(name='Менеджеры')

        # Добавляем права для менеджеров
        content_type = ContentType.objects.get_for_model(Mailing)
        permissions = Permission.objects.filter(content_type=content_type)
        for perm in permissions:
            if perm.codename in ['view_all_mailings', 'disable_mailings']:
                managers_group.permissions.add(perm)

        content_type = ContentType.objects.get_for_model(Message)
        permissions = Permission.objects.filter(content_type=content_type)
        for perm in permissions:
            if perm.codename == 'view_all_messages':
                managers_group.permissions.add(perm)

        content_type = ContentType.objects.get_for_model(Client)
        permissions = Permission.objects.filter(content_type=content_type)
        for perm in permissions:
            if perm.codename == 'view_all_clients':
                managers_group.permissions.add(perm)

        self.stdout.write(self.style.SUCCESS('Successfully initialized groups and permissions'))
