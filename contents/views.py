from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from accounts.models import Notification
from .models import Content, Comment, Reaction, Vote, Wishlist, Purchase, SiteConfig
from .forms import ContentForm, ContentEditForm, CommentForm, PasswordVerifyForm


def _notify_vote_milestone(content):
    """투표 49개 달성 시 알림 발송"""
    total = content.total_vote_count
    if total != settings.VOTE_NOTIFY_THRESHOLD:
        return

    msg = f'"{content.title}"의 투표가 {total}개를 달성했습니다!'
    link = f'/content/{content.pk}/'

    # 로그인 회원 작성자에게 인앱 알림
    if content.author:
        Notification.objects.get_or_create(
            user=content.author,
            message=msg,
            defaults={'link': link},
        )

    # 이메일 알림 (작성자 이메일 또는 별도 입력 이메일)
    email = ''
    if content.author and content.author.email:
        email = content.author.email
    elif content.author_email:
        email = content.author_email

    if email:
        try:
            send_mail(
                subject=f'[해방일지] 투표 알림 — {content.title}',
                message=(
                    f'안녕하세요!\n\n'
                    f'"{content.title}" 게시물의 투표가 {total}개를 달성했습니다.\n\n'
                    f'지금 확인하러 가기: https://djangotext.onrender.com{link}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass


def home(request):
    from django.utils import timezone
    featured = Content.objects.filter(
        status='approved', featured_until__gt=timezone.now()
    ).select_related('author')
    normal = Content.objects.filter(
        status='approved', featured_until__isnull=True
    ).select_related('author') | Content.objects.filter(
        status='approved', featured_until__lte=timezone.now()
    ).select_related('author')

    contents = list(featured) + list(normal.order_by('-created_at'))
    paginator = Paginator(contents, 12)
    page = request.GET.get('page', 1)
    contents_page = paginator.get_page(page)
    return render(request, 'home.html', {'contents': contents_page})


def temporary_storage(request):
    contents = Content.objects.filter(
        status='approved', category='temporary_storage'
    ).select_related('author')

    user_votes = {}
    if request.user.is_authenticated:
        votes = Vote.objects.filter(
            content__in=contents, user=request.user
        ).values_list('content_id', 'vote_type')
        user_votes = dict(votes)

    return render(request, 'contents/temporary.html', {
        'contents': contents,
        'user_votes': user_votes,
    })


def exhibition(request):
    contents = Content.objects.filter(
        status='approved', category='immediate_exhibition'
    ).select_related('author')

    user_wishlists = set()
    if request.user.is_authenticated:
        user_wishlists = set(
            Wishlist.objects.filter(
                content__in=contents, user=request.user
            ).values_list('content_id', flat=True)
        )

    return render(request, 'contents/exhibition.html', {
        'contents': contents,
        'user_wishlists': user_wishlists,
    })


def detail(request, pk):
    content = get_object_or_404(Content, pk=pk, status='approved')

    if not request.user.is_authenticated:
        return render(request, 'contents/detail_guest.html', {'content': content})

    comments = content.comments.select_related('author').all()
    comment_form = CommentForm()

    user_reactions = set(
        Reaction.objects.filter(
            content=content, user=request.user
        ).values_list('reaction_type', flat=True)
    )
    vote = Vote.objects.filter(content=content, user=request.user).first()
    user_vote = vote.vote_type if vote else None
    user_wishlisted = Wishlist.objects.filter(content=content, user=request.user).exists()

    # 상점 아이템 보유 여부
    has_jury_summon = Purchase.objects.filter(
        user=request.user, item_type='jury_summon', used=False
    ).exists() if content.category == 'temporary_storage' else False

    return render(request, 'contents/detail.html', {
        'content': content,
        'comments': comments,
        'comment_form': comment_form,
        'user_reactions': user_reactions,
        'user_vote': user_vote,
        'user_wishlisted': user_wishlisted,
        'has_jury_summon': has_jury_summon,
    })


@login_required
def create(request):
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.set_password(form.cleaned_data['password'])
            content.author = request.user
            content.author_email = form.cleaned_data.get('author_email', '')
            config = SiteConfig.get()
            if config.user_needs_approval(request.user):
                content.status = 'pending'
                msg = '해방일지가 등록되었습니다! 관리자 승인 후 아카이브에 공개됩니다.'
            else:
                content.status = 'approved'
                msg = '해방일지가 등록되었습니다!'
                request.user.add_points('upload')
            content.save()
            messages.success(request, msg)
            return redirect('home')
    else:
        form = ContentForm()
        form.fields['nickname'].initial = request.user.username

    return render(request, 'contents/create.html', {
        'form': form,
        'VOTE_NOTIFY_THRESHOLD': settings.VOTE_NOTIFY_THRESHOLD,
    })


def edit_verify(request, pk):
    content = get_object_or_404(Content, pk=pk)

    if request.method == 'POST':
        verify_form = PasswordVerifyForm(request.POST)
        if verify_form.is_valid():
            if content.verify_password(verify_form.cleaned_data['password']):
                request.session[f'edit_verified_{pk}'] = True
                return redirect('edit_content', pk=pk)
            else:
                messages.error(request, '비밀번호가 올바르지 않습니다.')
    else:
        verify_form = PasswordVerifyForm()

    return render(request, 'contents/edit_verify.html', {
        'verify_form': verify_form,
        'content': content,
    })


def edit(request, pk):
    content = get_object_or_404(Content, pk=pk)

    if not request.session.get(f'edit_verified_{pk}'):
        return redirect('edit_verify', pk=pk)

    if request.method == 'POST':
        form = ContentEditForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.status = 'pending'
            updated.save()
            del request.session[f'edit_verified_{pk}']
            messages.success(request, '수정이 완료되었습니다. 관리자 승인 후 반영됩니다.')
            return redirect('home')
    else:
        form = ContentEditForm(instance=content)

    return render(request, 'contents/edit.html', {'form': form, 'content': content})


@login_required
@require_POST
def add_comment(request, pk):
    content = get_object_or_404(Content, pk=pk, status='approved')
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.content = content
        comment.author = request.user
        comment.save()
        request.user.add_points('comment')
    return redirect('detail', pk=pk)


@login_required
@require_POST
def toggle_reaction(request, pk):
    content = get_object_or_404(Content, pk=pk, status='approved')
    reaction_type = request.POST.get('reaction_type')

    if reaction_type not in ['empathy', 'sad', 'angry']:
        return JsonResponse({'error': '잘못된 반응 유형'}, status=400)

    reaction, created = Reaction.objects.get_or_create(
        content=content, user=request.user, reaction_type=reaction_type
    )
    if not created:
        reaction.delete()
        active = False
    else:
        request.user.add_points('reaction')
        active = True

    return JsonResponse({
        'active': active,
        'reaction_type': reaction_type,
        'counts': {
            'empathy': content.empathy_count,
            'sad': content.sad_count,
            'angry': content.angry_count,
        }
    })


@login_required
@require_POST
def cast_vote(request, pk):
    content = get_object_or_404(Content, pk=pk, status='approved', category='temporary_storage')
    vote_type = request.POST.get('vote_type')

    if vote_type not in ['throw', 'keep']:
        return JsonResponse({'error': '잘못된 투표 유형'}, status=400)

    # 대법관의 망치 보유 여부 확인
    hammer = Purchase.objects.filter(
        user=request.user, item_type='judge_hammer', used=False
    ).first()
    weight = 3 if hammer else 1

    vote, created = Vote.objects.get_or_create(
        content=content, user=request.user,
        defaults={'vote_type': vote_type, 'weight': weight}
    )
    if not created:
        if vote.vote_type == vote_type:
            vote.delete()
            current_vote = None
        else:
            vote.vote_type = vote_type
            vote.weight = weight
            vote.save()
            current_vote = vote_type
    else:
        if hammer:
            hammer.used = True
            hammer.used_on = content
            hammer.save()
        request.user.add_points('vote')
        current_vote = vote_type
        _notify_vote_milestone(content)

    return JsonResponse({
        'current_vote': current_vote,
        'throw_count': content.throw_vote_count,
        'keep_count': content.keep_vote_count,
    })


@login_required
@require_POST
def toggle_wishlist(request, pk):
    content = get_object_or_404(Content, pk=pk, status='approved', category='immediate_exhibition')

    existing = Wishlist.objects.filter(content=content, user=request.user).first()
    if existing:
        existing.delete()
        wishlisted = False
    else:
        if not content.can_add_wishlist:
            return JsonResponse({'error': '찜 인원이 가득 찼습니다 (최대 3명).'}, status=400)
        Wishlist.objects.create(content=content, user=request.user)
        request.user.add_points('wishlist')
        wishlisted = True

    return JsonResponse({
        'wishlisted': wishlisted,
        'wishlist_count': content.wishlist_count,
        'can_add': content.can_add_wishlist,
    })


# ── 상점 ──────────────────────────────────────────────────

@login_required
def store_index(request):
    if request.user.level < 1:
        messages.error(request, 'Level 1 이상 회원만 상점을 이용할 수 있습니다.')
        return redirect('home')

    my_items = Purchase.objects.filter(user=request.user, used=False)
    return render(request, 'store/index.html', {
        'my_items': my_items,
        'price': settings.STORE_ITEM_PRICE,
    })


@login_required
@require_POST
def buy_item(request):
    item_type = request.POST.get('item_type')
    if item_type not in ['jury_summon', 'judge_hammer']:
        return JsonResponse({'error': '잘못된 아이템'}, status=400)

    price = settings.STORE_ITEM_PRICE
    if not request.user.spend_points(price):
        return JsonResponse({'error': f'포인트가 부족합니다. (필요: {price}pt)'}, status=400)

    from accounts.models import PointHistory
    PointHistory.objects.create(user=request.user, action='spend', points=-price)
    Purchase.objects.create(user=request.user, item_type=item_type)

    return JsonResponse({
        'success': True,
        'remaining_points': request.user.points,
        'item_label': dict(Purchase.ITEMS)[item_type],
    })


@login_required
@require_POST
def use_jury_summon(request, pk):
    content = get_object_or_404(Content, pk=pk)
    purchase = Purchase.objects.filter(
        user=request.user, item_type='jury_summon', used=False
    ).first()

    if not purchase:
        messages.error(request, '배심원 소환권이 없습니다.')
        return redirect('store_index')

    content.featured_until = timezone.now() + timedelta(hours=24)
    content.save(update_fields=['featured_until'])
    purchase.used = True
    purchase.used_on = content
    purchase.save()
    messages.success(request, f'"{content.title}"이(가) 24시간 동안 메인 최상단에 노출됩니다!')
    return redirect('detail', pk=pk)
