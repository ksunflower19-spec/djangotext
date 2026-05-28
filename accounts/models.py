from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    MEMBER_TYPES = [
        ('regular', '일반 회원'),
        ('project', '프로젝트 멤버'),
    ]
    member_type = models.CharField(max_length=20, choices=MEMBER_TYPES, default='regular')
    points = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True, verbose_name='자기소개')

    class Meta:
        verbose_name = '회원'
        verbose_name_plural = '회원 목록'

    def __str__(self):
        return f"{self.username} ({self.get_member_type_display()})"

    def add_points(self, action):
        point_map = {
            'register': 10,
            'upload': 50,
            'comment': 5,
            'reaction': 2,
            'wishlist': 5,
            'vote': 2,
        }
        earned = point_map.get(action, 0)
        if earned:
            self.points += earned
            self.save(update_fields=['points'])
            PointHistory.objects.create(user=self, action=action, points=earned)
        return earned


class PointHistory(models.Model):
    ACTIONS = [
        ('register', '회원가입'),
        ('upload', '콘텐츠 업로드'),
        ('comment', '댓글 작성'),
        ('reaction', '반응 남기기'),
        ('wishlist', '찜하기'),
        ('vote', '투표하기'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_history')
    action = models.CharField(max_length=50, choices=ACTIONS)
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '포인트 내역'
        verbose_name_plural = '포인트 내역 목록'
