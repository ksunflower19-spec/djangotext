from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PointHistory, ProjectCode, Notification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'member_type', 'points', 'total_points', 'level_display', 'date_joined', 'is_active']
    list_filter = ['member_type', 'is_active', 'is_staff']
    readonly_fields = ['level_display']
    fieldsets = UserAdmin.fieldsets + (
        ('포인트 & 레벨', {'fields': ('points', 'total_points', 'level_display')}),
        ('회원 정보', {'fields': ('member_type', 'project_group', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('회원 정보', {'fields': ('member_type',)}),
    )

    @admin.display(description='레벨')
    def level_display(self, obj):
        lv = obj.total_points // 1000
        return f'Lv.{lv}' if lv > 0 else 'Lv.0'


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
