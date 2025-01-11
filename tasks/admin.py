from django.contrib import admin
from tasks.models import Category, Task, Sending_Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'name'
    )
    list_filter = (
        'id',
        'user',
        'name'
    )
    search_fields = (
        'id',
        'user',
        'name'
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'annotation',
        'user',
        'status',
        'category'
    )
    list_display_links = (
        'id',
        'name'
    )
    list_filter = (
        'id',
        'name',
        'annotation',
        'user',
        'status',
        'category'
    )
    search_fields = (
        'id',
        'name',
        'annotation',
        'user',
        'status',
        'category'
    )
    fieldsets = (
        (None, {
            'fields': ('name', 'user', 'status')
        }),
        ('Annotation', {
            'fields': ('annotation',)
        }),
        ('Category', {
            'fields': ('category', )
        }),
    )


@admin.register(Sending_Task)
class Sending_TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'task',
        'time_for_send',
        'period',
        'status',
        'day_start_sending',
        'last_send'
    )
    fields = [
        'task',
        ('time_for_send', 'period',),
        'status'
    ]
