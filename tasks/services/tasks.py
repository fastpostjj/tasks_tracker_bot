from django.db.models import Q
from tasks.models import Task, Category
from user_auth.models import User


class TaskConnector():
    '''
    Класс TaskConnector для работы с задачами. Создает задачу, редактирует и удаляет.

    '''
    def is_user_exsist(self, chat_id):
        """
        Проверка существования пользователя с данным chat_id
        """
        try:
            flag = User.objects.filter(chat_id=chat_id).exists()
        except User.DoesNotExist:
            flag = False
        return flag

    def is_category_exist(self, **kwargs):
        """
        Проверка существования категории с данным названием
        для данного пользователя
        """
        flag = False
        chat_id = kwargs.get('chat_id')
        name = kwargs.get('name')
        if self.is_user_exsist(chat_id):
            try:
                user = User.objects.get(chat_id=chat_id)
                flag = Category.objects.filter(
                    Q(user=user) & Q(name=name)
                    ).exists()
            except Category.DoesNotExist:
                print(f"Category {name} DoesNotExist")
        return flag

    def create_user(self, chat_id):
        user = User.objects.create(
            chat_id=chat_id,
            # first_name='User',
            # last_name='Just User',
            is_staff=False,
            is_superuser=False
        )
        user.set_password('111111111')
        user.save()

    def create_category(self, **kwargs) -> str:
        name = kwargs.get('name')
        chat_id = kwargs.get('chat_id')
        if self.is_user_exsist(chat_id):
            user = User.objects.get(chat_id=chat_id)
        else:
            user = self.create_user(chat_id)

        if self.is_category_exist(chat_id=chat_id, name=name):
            return f'Категория {name} уже существует'
        else:
            Category.objects.create(user=user, name=name)
            return f'Категория {name} создана'

    def create_task(self, **kwargs):
        chat_id = kwargs.get('chat_id')
        name = kwargs.get('name')
        annotation = kwargs.get('annotation')
        status = 'CREATED'
        category_id = kwargs.get('category')
        if name and name != "":
            if category_id:
                category = Category.objects.get(id=category_id)
            else:
                category = None

            if self.is_user_exsist(chat_id):
                user = User.objects.get(chat_id=chat_id)
            else:
                user = self.create_user(chat_id)
            task = Task.objects.create(
                user=user,
                name=name,
                annotation=annotation,
                status=status,
                category=category
            )
            return task

    def get_user_tasks(self, chat_id):
        if self.is_user_exsist(chat_id):
            # user = User.objects.get(chat_id=chat_id)
            tasks = Task.objects.values(
                'id',
                'name',
                'annotation',
                'status',
                # 'is_group',
                # 'group',
                # 'group__name'
                ).filter(user__chat_id=chat_id)  # .order_by('group')
            return tasks

    def get_user_categories(self, chat_id):
        if self.is_user_exsist(chat_id):
            category = Category.objects.values(
                'id',
                'name',
                'user'
                ).filter(user__chat_id=chat_id)
            return category

    def list_tasks(self, chat_id, category_id):
        if self.is_user_exsist(chat_id):
            tasks = Task.objects.values(
                'id',
                'name',
                'annotation',
                'status',
                'category__name',
                ).filter(Q(user__chat_id=chat_id) & Q(category__id=category_id))
            return tasks
