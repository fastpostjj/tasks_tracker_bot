from django.core.management import BaseCommand

from user_auth.models import User


class Command(BaseCommand):
    """
   Создаем суперпользователя, менеджера и обычного пользователя
   с id 1, 2, 3
    """

    def create_superuser(self, *args, **options):
        user = User.objects.create(
            chat_id=1,
            # email='admin@admin.pro',
            first_name='Admin',
            last_name='SuperAdmin',
            is_staff=True,
            is_superuser=True
        )
        user.set_password('123abc123')
        user.save()

    def create_user(self, *args, **options):
        user = User.objects.create(
            chat_id=3,
            first_name='User',
            last_name='Just User',
            is_staff=False,
            is_superuser=False
        )
        user.set_password('123abc123')
        user.save()

    def create_manager(self, *args, **options):
        user = User.objects.create(
            # email='manager@manager.ru',
            chat_id=2,
            first_name='manager',
            last_name='moderator',
            is_staff=True,
            is_superuser=False
        )
        user.set_password('123abc123')
        user.save()

    def change_password(self, *args, **options):
        user = User.objects.get(chat_id=2)
        user.set_password('123abc123')

        user.save()

    def handle(self, *args, **options):
        self.create_superuser(*args, **options)
        self.create_manager(*args, **options)
        self.create_user(*args, **options)
        # self.change_password(*args, **options)
