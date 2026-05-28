from django.db import models
from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password as _check_password

User = get_user_model()


class Content(models.Model):
    CATEGORIES = [
        ('immediate_trash', '즉시해방 — 직접 버리기'),
        ('immediate_exhibition', '즉시해방 — 실물전시 참여'),
        ('temporary_storage', '임시보관'),
    ]
    STATUS = [
        ('pending', '승인 대기'),
        ('approved', '승인됨'),
        ('rejected', '거절됨'),
    ]

    title = models.CharField(max_length=200, verbose_name='반려쓰레기 이름')
    story = models.TextField(verbose_name='해방일지')
    image = models.ImageField(upload_to='contents/%Y/%m/', verbose_name='사진')
    nickname = models.CharField(max_length=50, verbose_name='닉네임')
    password_hash = models.CharField(max_length=256, verbose_name='수정용 비밀번호')
    author_email = models.EmailField(blank=True, verbose_name='알림 이메일 (선택)')
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='contents', verbose_name='작성자 계정'
    )
    category = models.CharField(max_length=30, choices=CATEGORIES, verbose_name='카테고리')
    status = models.CharField(max_length=20, choices=STATUS, default='pending', verbose_name='승인 상태')
    featured_until = models.DateTimeField(null=True, blank=True, verbose_name='상단 노출 만료 시각')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '해방일지'
        verbose_name_plural = '해방일지 목록'

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title} — {self.nickname}"

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def verify_password(self, raw_password):
        return _check_password(raw_password, self.password_hash)

    @property
    def is_featured(self):
        from django.utils import timezone
        return self.featured_until and self.featured_until > timezone.now()

    @property
    def empathy_count(self):
        return self.reactions.filter(reaction_type='empathy').count()

    @property
    def sad_count(self):
        return self.reactions.filter(reaction_type='sad').count()

    @property
    def angry_count(self):
        return self.reactions.filter(reaction_type='angry').count()

    @property
    def wishlist_count(self):
        return self.wishlists.count()

    @property
    def can_add_wishlist(self):
        return self.wishlists.count() < 3

    @property
    def throw_vote_count(self):
        result = self.votes.filter(vote_type='throw').aggregate(total=Sum('weight'))
        return result['total'] or 0

    @property
    def keep_vote_count(self):
        result = self.votes.filter(vote_type='keep').aggregate(total=Sum('weight'))
        return result['total'] or 0

    @property
    def total_vote_count(self):
        return self.throw_vote_count + self.keep_vote_count


class Comment(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(verbose_name='댓글')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = '댓글'
        verbose_name_plural = '댓글 목록'


class Reaction(models.Model):
    REACTION_TYPES = [
        ('empathy', '공감'),
        ('sad', '슬픔'),
        ('angry', '화남'),
    ]
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES)

    class Meta:
        unique_together = ['content', 'user', 'reaction_type']
        verbose_name = '반응'
        verbose_name_plural = '반응 목록'


class Vote(models.Model):
    VOTE_TYPES = [
        ('throw', '버려라'),
        ('keep', '아직은 말아라'),
    ]
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=20, choices=VOTE_TYPES)
    weight = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = ['content', 'user']
        verbose_name = '투표'
        verbose_name_plural = '투표 목록'


class Wishlist(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='wishlists')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['content', 'user']
        verbose_name = '찜'
        verbose_name_plural = '찜 목록'


class Purchase(models.Model):
    ITEMS = [
        ('jury_summon', '배심원 소환권'),
        ('judge_hammer', '대법관의 망치'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    item_type = models.CharField(max_length=30, choices=ITEMS)
    used = models.BooleanField(default=False)
    used_on = models.ForeignKey(
        Content, null=True, blank=True, on_delete=models.SET_NULL, related_name='featured_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '상점 구매 내역'
        verbose_name_plural = '상점 구매 내역 목록'
