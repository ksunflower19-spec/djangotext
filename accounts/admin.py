from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PointHistory, ProjectCode, Notification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'member_type', 'points', 'date_joined', 'is_active']
    list_filter = ['member_type', 'is_active', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('member_type', 'points', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('추가 정보', {'fields': ('member_type',)}),
    )


@admin.register(PointHistory)
class PointHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'points', 'created_at']
    list_filter = ['action']
    readonly_fields = ['created_at']


@admin.register(ProjectCode)
class ProjectCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'group_name', 'description']
    search_fields = ['code', 'group_name']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read']
    readonly_fields = ['created_at']
