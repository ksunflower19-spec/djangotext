from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PointHistory


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
