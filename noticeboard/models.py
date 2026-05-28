from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminPost(models.Model):
    title = models.CharField(max_length=200, verbose_name='제목')
    body = models.TextField(verbose_name='내용 (마크다운 지원)')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_posts')
    is_pinned = models.BooleanField(default=False, verbose_name='상단 고정')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']
        verbose_name = '운영 게시글'
        verbose_name_plural = '운영 게시글 목록'

    def __str__(self):
        return self.title


class AdminComment(models.Model):
    post = models.ForeignKey(AdminPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_comments')
    text = models.TextField(verbose_name='댓글')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = '운영 댓글'
        verbose_name_plural = '운영 댓글 목록'
