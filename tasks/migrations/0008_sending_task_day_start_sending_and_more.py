# Generated by Django 5.1.4 on 2025-01-11 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_category_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='sending_task',
            name='day_start_sending',
            field=models.DateField(blank=True, null=True, verbose_name='Дата начала рассылки задачи'),
        ),
        migrations.AddField(
            model_name='sending_task',
            name='last_send',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата и время последней отправки'),
        ),
        migrations.AlterField(
            model_name='sending_task',
            name='period',
            field=models.CharField(blank=True, choices=[('DAILY', 'Ежедневно'), ('WEEKLY', 'Еженедельно'), ('MONTHLY', 'Ежемесячно'), ('YEARLY', 'Ежегодно'), ('CUSTOM_DAY', 'Однократно')], default='WEEKLY', max_length=19, null=True, verbose_name='Периодичность рассылки задачи'),
        ),
    ]
