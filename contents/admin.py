from django.contrib import admin
from django.utils.html import format_html
from .models import Content, Comment, Reaction, Vote, Wishlist, SiteConfig


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'nickname', 'category', 'status', 'image_preview', 'reaction_summary', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'story', 'nickname']
    readonly_fields = ['created_at', 'updated_at', 'image_preview', 'reaction_summary']
    actions = ['approve_contents', 'reject_contents']
    ordering = ['-created_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'nickname', 'category', 'status', 'author')
        }),
        ('콘텐츠', {
            'fields': ('image', 'image_preview', 'story')
        }),
        ('날짜', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:4px;">',
                obj.image.url
            )
        return '—'
    image_preview.short_description = '미리보기'

    def reaction_summary(self, obj):
        return f"🫂 {obj.empathy_count}  😢 {obj.sad_count}  😤 {obj.angry_count}"
    reaction_summary.short_description = '반응'

    @admin.action(description='✅ 선택한 콘텐츠 승인')
    def approve_contents(self, request, queryset):
        updated = queryset.update(status='approved')
        for content in queryset.filter(author__isnull=False):
            content.author.add_points('upload')
        self.message_user(request, f'{updated}개의 콘텐츠가 승인되었습니다.')

    @admin.action(description='❌ 선택한 콘텐츠 거절')
    def reject_contents(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated}개의 콘텐츠가 거절되었습니다.')


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['content', 'author', 'text_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'author__username']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = '댓글 내용'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['content', 'user', 'vote_type']
    list_filter = ['vote_type']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['content', 'user', 'created_at']
    list_filter = ['created_at']
