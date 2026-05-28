from django.contrib import admin
from .models import AdminPost, AdminComment


@admin.register(AdminPost)
class AdminPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_pinned', 'created_at']
    list_filter = ['is_pinned']
    search_fields = ['title', 'body']


@admin.register(AdminComment)
class AdminCommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'created_at']
