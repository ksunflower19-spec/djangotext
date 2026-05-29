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
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments')
    guest_nickname = models.CharField(max_length=50, blank=True, verbose_name='비회원 닉네임')
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


class SiteConfig(models.Model):
    require_approval = models.BooleanField(
        default=True, verbose_name='콘텐츠 업로드 시 관리자 승인 필요'
    )
    auto_approve_groups = models.CharField(
        max_length=500, blank=True,
        verbose_name='자동 승인 그룹 (쉼표로 구분)',
        help_text='이 그룹에 속한 회원은 승인 없이 바로 공개됩니다. 예: 1기참여자, 운영팀',
    )
    # 비회원 글쓰기
    write_public = models.BooleanField(default=False, verbose_name='비회원 글쓰기 허용')
    # 아카이브 (즉시해방-직접버리기)
    archive_read_public = models.BooleanField(default=False, verbose_name='읽기')
    archive_comment_public = models.BooleanField(default=False, verbose_name='댓글')
    archive_reaction_public = models.BooleanField(default=False, verbose_name='반응')
    # 임시저장소
    temporary_read_public = models.BooleanField(default=False, verbose_name='읽기')
    temporary_comment_public = models.BooleanField(default=False, verbose_name='댓글')
    temporary_reaction_public = models.BooleanField(default=False, verbose_name='반응')
    # 실물전시
    exhibition_read_public = models.BooleanField(default=False, verbose_name='읽기')
    exhibition_comment_public = models.BooleanField(default=False, verbose_name='댓글')
    exhibition_reaction_public = models.BooleanField(default=False, verbose_name='반응')
    exhibition_wishlist_public = models.BooleanField(default=False, verbose_name='찜')

    class Meta:
        verbose_name = '사이트 설정'
        verbose_name_plural = '사이트 설정'

    def __str__(self):
        return '사이트 설정'

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def user_needs_approval(self, user):
        if not self.require_approval:
            return False
        if user and getattr(user, 'is_authenticated', False) and getattr(user, 'project_group', None):
            allowed = [g.strip() for g in self.auto_approve_groups.split(',') if g.strip()]
            if user.project_group in allowed:
                return False
        return True

    def can_public_read(self, category):
        return {
            'immediate_trash': self.archive_read_public,
            'immediate_exhibition': self.exhibition_read_public,
            'temporary_storage': self.temporary_read_public,
        }.get(category, False)

    def can_public_comment(self, category):
        return {
            'immediate_trash': self.archive_comment_public,
            'immediate_exhibition': self.exhibition_comment_public,
            'temporary_storage': self.temporary_comment_public,
        }.get(category, False)

    def can_public_reaction(self, category):
        return {
            'immediate_trash': self.archive_reaction_public,
            'immediate_exhibition': self.exhibition_reaction_public,
            'temporary_storage': self.temporary_reaction_public,
        }.get(category, False)


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
