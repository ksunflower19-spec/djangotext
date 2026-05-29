from django.contrib import admin
from django.contrib import messages as admin_messages
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html
from .models import Content, Comment, Reaction, Vote, Wishlist, SiteConfig


PUBLIC_FIELDS = [
    'write_public',
    'archive_read_public', 'archive_comment_public', 'archive_reaction_public',
    'temporary_read_public', 'temporary_comment_public', 'temporary_reaction_public',
    'exhibition_read_public', 'exhibition_comment_public', 'exhibition_reaction_public',
    'exhibition_wishlist_public',
]


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
    readonly_fields = ['quick_toggle_buttons']
    fieldsets = (
        ('콘텐츠 승인', {
            'fields': ('require_approval', 'auto_approve_groups'),
        }),
        ('비회원 권한 빠른 설정', {
            'fields': ('quick_toggle_buttons',),
            'description': '아래 버튼으로 비회원 권한을 한꺼번에 켜거나 끌 수 있습니다.',
        }),
        ('비회원 글쓰기', {
            'fields': ('write_public',),
            'description': '체크하면 로그인 없이도 해방일지를 기록할 수 있습니다.',
        }),
        ('비회원 권한 — 아카이브 (즉시해방·직접버리기)', {
            'fields': ('archive_read_public', 'archive_comment_public', 'archive_reaction_public'),
        }),
        ('비회원 권한 — 임시저장소', {
            'fields': ('temporary_read_public', 'temporary_comment_public', 'temporary_reaction_public'),
        }),
        ('비회원 권한 — 실물전시', {
            'fields': ('exhibition_read_public', 'exhibition_comment_public', 'exhibition_reaction_public', 'exhibition_wishlist_public'),
        }),
    )

    def quick_toggle_buttons(self, obj):
        allow_url = reverse('admin:siteconfig_allow_all', args=[obj.pk])
        disallow_url = reverse('admin:siteconfig_disallow_all', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}" style="background:#417690;color:#fff;padding:6px 14px;border-radius:4px;text-decoration:none;margin-right:8px;">모두 허용</a>'
            '<a class="button" href="{}" style="background:#ba2121;color:#fff;padding:6px 14px;border-radius:4px;text-decoration:none;">모두 허용하지 않음</a>',
            allow_url, disallow_url,
        )
    quick_toggle_buttons.short_description = '비회원 권한 일괄 설정'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('<int:pk>/allow_all/', self.admin_site.admin_view(self._allow_all_view), name='siteconfig_allow_all'),
            path('<int:pk>/disallow_all/', self.admin_site.admin_view(self._disallow_all_view), name='siteconfig_disallow_all'),
        ]
        return custom + urls

    def _allow_all_view(self, request, pk):
        SiteConfig.objects.filter(pk=pk).update(**{f: True for f in PUBLIC_FIELDS})
        admin_messages.success(request, '모든 비회원 권한이 허용되었습니다.')
        return redirect(reverse('admin:contents_siteconfig_change', args=[pk]))

    def _disallow_all_view(self, request, pk):
        SiteConfig.objects.filter(pk=pk).update(**{f: False for f in PUBLIC_FIELDS})
        admin_messages.success(request, '모든 비회원 권한이 차단되었습니다.')
        return redirect(reverse('admin:contents_siteconfig_change', args=[pk]))

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
