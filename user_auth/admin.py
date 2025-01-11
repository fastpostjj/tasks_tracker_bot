from django.contrib import admin
from user_auth.models import User


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'chat_id',
        'first_name',
        'last_name',
        'is_subscripted',
        'phone',
        'is_active'
    )

    list_display_links = (
        'id',
        'chat_id',
        'is_subscripted',
        'phone'
    )
    list_filter = (
        'id',
        'chat_id',
        'is_subscripted',
        'phone'
    )
    search_fields = (
        'id',
        'chat_id',
        'is_subscripted',
        'phone'
    )