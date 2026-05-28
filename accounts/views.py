from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import RegisterForm, LoginForm
from .models import Notification, ProjectCode


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            member_type = form.cleaned_data['member_type']
            code_input = form.cleaned_data.get('project_code', '').strip()
            user.member_type = member_type
            if member_type == 'project' and code_input:
                try:
                    pc = ProjectCode.objects.get(code=code_input)
                    user.project_group = pc.group_name
                except ProjectCode.DoesNotExist:
                    pass
            user.save()
            user.add_points('register')
            login(request, user)
            messages.success(request, f'환영합니다, {user.username}님! 가입 포인트 10pt가 지급되었습니다.')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    contents = user.contents.order_by('-created_at')
    recent_points = user.point_history.all()[:10]
    purchases = user.purchases.filter(used=False)
    return render(request, 'accounts/profile.html', {
        'profile_user': user,
        'contents': contents,
        'recent_points': recent_points,
        'purchases': purchases,
    })


@login_required
def notifications_view(request):
    notifications = request.user.notifications.all()[:30]
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'accounts/notifications.html', {'notifications': notifications})


@login_required
@require_POST
def mark_notification_read(request, pk):
    Notification.objects.filter(pk=pk, user=request.user).update(is_read=True)
    return JsonResponse({'ok': True})
