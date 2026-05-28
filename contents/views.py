from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Content, Comment, Reaction, Vote, Wishlist
from .forms import ContentForm, ContentEditForm, CommentForm, PasswordVerifyForm


def home(request):
    contents = Content.objects.filter(status='approved').select_related('author')
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
    comments = content.comments.select_related('author').all()
    comment_form = CommentForm()

    user_reactions = set()
    user_vote = None
    user_wishlisted = False

    if request.user.is_authenticated:
        user_reactions = set(
            Reaction.objects.filter(
                content=content, user=request.user
            ).values_list('reaction_type', flat=True)
        )
        vote = Vote.objects.filter(content=content, user=request.user).first()
        user_vote = vote.vote_type if vote else None
        user_wishlisted = Wishlist.objects.filter(content=content, user=request.user).exists()

    return render(request, 'contents/detail.html', {
        'content': content,
        'comments': comments,
        'comment_form': comment_form,
        'user_reactions': user_reactions,
        'user_vote': user_vote,
        'user_wishlisted': user_wishlisted,
    })


def create(request):
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.set_password(form.cleaned_data['password'])
            if request.user.is_authenticated:
                content.author = request.user
            content.save()
            messages.success(request, '해방일지가 등록되었습니다! 관리자 승인 후 아카이브에 공개됩니다.')
            return redirect('home')
    else:
        form = ContentForm()
        if request.user.is_authenticated:
            form.fields['nickname'].initial = request.user.username

    return render(request, 'contents/create.html', {'form': form})


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
        return JsonResponse({'error': '잘못된 반응 유형입니다.'}, status=400)

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
        return JsonResponse({'error': '잘못된 투표 유형입니다.'}, status=400)

    vote, created = Vote.objects.get_or_create(
        content=content, user=request.user,
        defaults={'vote_type': vote_type}
    )
    if not created:
        if vote.vote_type == vote_type:
            vote.delete()
            current_vote = None
        else:
            vote.vote_type = vote_type
            vote.save()
            current_vote = vote_type
    else:
        request.user.add_points('vote')
        current_vote = vote_type

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
