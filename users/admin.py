from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# Register your models here.
from .models import CustomUser, ReadingHistory, Notification


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional info', {
            'fields': ('middle_name', 'avatar')
        }),
    )

    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'middle_name')
    list_display_links = ('id', 'username', 'email')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'middle_name')
    list_filter = ('last_login', 'date_joined', 'is_staff', 'is_superuser', 'is_active')


@admin.register(ReadingHistory)
class ReadingHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user','message','created_at']