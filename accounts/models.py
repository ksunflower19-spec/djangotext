from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    MEMBER_TYPES = [
        ('regular', '일반 회원'),
        ('project', '프로젝트 참여회원'),
    ]
    member_type = models.CharField(max_length=20, choices=MEMBER_TYPES, default='regular')
    project_group = models.CharField(max_length=100, blank=True, verbose_name='프로젝트 그룹')
    points = models.PositiveIntegerField(default=0, verbose_name='사용 가능 포인트')
    total_points = models.PositiveIntegerField(default=0, verbose_name='누적 포인트 (레벨 기준)')
    bio = models.TextField(blank=True, verbose_name='자기소개')

    class Meta:
        verbose_name = '회원'
        verbose_name_plural = '회원 목록'

    def __str__(self):
        return f"{self.username} ({self.get_member_type_display()})"

    @property
    def level(self):
        return self.total_points // 1000

    @property
    def level_label(self):
        lv = self.level
        return f"Lv.{lv}" if lv > 0 else ""

    @property
    def level_progress(self):
        return (self.total_points % 1000) // 10

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
            self.total_points += earned
            self.save(update_fields=['points', 'total_points'])
            PointHistory.objects.create(user=self, action=action, points=earned)
        return earned

    def spend_points(self, amount):
        if self.points < amount:
            return False
        self.points -= amount
        self.save(update_fields=['points'])
        return True


class PointHistory(models.Model):
    ACTIONS = [
        ('register', '회원가입'),
        ('upload', '콘텐츠 업로드'),
        ('comment', '댓글 작성'),
        ('reaction', '반응 남기기'),
        ('wishlist', '찜하기'),
        ('vote', '투표하기'),
        ('spend', '포인트 사용'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_history')
    action = models.CharField(max_length=50, choices=ACTIONS)
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '포인트 내역'
        verbose_name_plural = '포인트 내역 목록'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=300)
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '알림'
        verbose_name_plural = '알림 목록'


class ProjectCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name='회원코드')
    group_name = models.CharField(max_length=100, verbose_name='그룹명')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = '프로젝트 코드'
        verbose_name_plural = '프로젝트 코드 목록'

    def __str__(self):
        return f"{self.code} → {self.group_name}"
