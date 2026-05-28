from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.add_points('register')
            login(request, user)
            messages.success(request, f'환영합니다, {user.username}님! 가입 축하 포인트 10점이 지급되었습니다.')
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
            messages.success(request, f'반갑습니다, {user.username}님!')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, '로그아웃되었습니다.')
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    contents = user.contents.order_by('-created_at')
    recent_points = user.point_history.all()[:10]

    return render(request, 'accounts/profile.html', {
        'profile_user': user,
        'contents': contents,
        'recent_points': recent_points,
    })
