from django.db import models
from config.settings import NULLABLE
from user_auth.models import User


STATUS = [
        ('CREATED', 'Создана'),
        ('WORK', 'В работе'),
        ('POSTPONED', 'Отложено'),
        ('READY', 'Выполнено'),
    ]
PERIOD = [
        ('DAILY', 'Ежедневно'),
        ('WEEKLY', 'Еженедельно'),
        ('MONTHLY', 'Ежемесячно'),
        ('YEARLY', 'Ежегодно'),
        ('CUSTOM_DAY', 'Однократно'),
    ]


class Category(models.Model):
    """
    Класс Category -категории задач
    """
    name = models.CharField(
        max_length=200,
        verbose_name="Задача",
    )
    user = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return f"{self.name}"


class Task(models.Model):
    """
    Задачи пользователей, которые будут рассылаться по расписанию
    name - название задачи,
    annotation - описание задачи,
    user - автор задачи,
    status - статус задачи,
    category - категория задачи
    """
    # is_group - является ли задача группой,
    # group - группа, к которой принадлежит задача

    name = models.CharField(
        max_length=200,
        verbose_name="Задача",
    )
    annotation = models.TextField(
        verbose_name="Описание задачи",
        **NULLABLE,
    )
    user = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=9,
        choices=STATUS,
        default='CREATED',
        **NULLABLE,
    )
    # is_group = models.BooleanField(
    #     verbose_name="Это группа",
    #     default=False
    # )
    # group = models.ForeignKey(
    #     'self',
    #     verbose_name="Группа",
    #     on_delete=models.DO_NOTHING,
    #     **NULLABLE,
    # )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.DO_NOTHING,
        **NULLABLE,
    )

    class Meta:
        verbose_name = 'задача'
        verbose_name_plural = 'задачи'

    def __str__(self):
        return f"{self.name}"

    def get_status(self):
        return f"{self.status}"

    def get_full_description(self):
        return f"Задача{self.name} {self.status}"


class Sending_Task(models.Model):
    """
    Класс Send_Task обеспечивает отправку задач/групп задач пользователям
    в телеграмм по заданному ими расписанию.
    task - задача,
    time_for_send - время рассылки задачи,
    day_start - дата начала рассылки,
    period - периодичность рассылки задачи,
    status - статус рассылки,
    last_send - дата и время последней отправки
    """
    task = models.ForeignKey(
        Task,
        verbose_name="Задача",
        on_delete=models.CASCADE
    )
    time_for_send = models.TimeField(
        verbose_name="Время рассылки задачи",
        **NULLABLE,
    )
    # day_start = models.DateField(
    #     verbose_name="Дата начала рассылки задачи",
    #     **NULLABLE,
    # )
    period = models.CharField(
        max_length=19,
        choices=PERIOD,
        default='WEEKLY',
        verbose_name="Периодичность рассылки задачи",
        **NULLABLE,
    )
    status = models.CharField(
        max_length=11,
        choices=[
            ('ACTIVE', 'Активна'),
            ('STOP', 'Завершена'),
            ('PAUSE', 'Остановлена'),
        ],
        default='ACTIVE',
        verbose_name="Статус рассылки задачи",
        **NULLABLE,
    )

    # last_send = models.DateTimeField(
    #     verbose_name="Дата и время последней отправки",
    #     **NULLABLE,
    # )

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'

    def __str__(self) -> str:
        return f'Рассылка {"группы задач" if self.task.is_group else "задачи"} {self.task} периодичность:{self.period} время: {self.time_for_send} статус: {self.status}'
