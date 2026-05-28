from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import AdminPost, AdminComment


def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


class PostForm(forms.ModelForm):
    class Meta:
        model = AdminPost
        fields = ['title', 'body', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'body': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 12}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = AdminComment
        fields = ['text']
        labels = {'text': ''}
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': '댓글을 입력하세요'}),
        }


@staff_required
def index(request):
    posts = AdminPost.objects.select_related('author').all()
    return render(request, 'noticeboard/index.html', {'posts': posts})


@staff_required
def detail(request, pk):
    post = get_object_or_404(AdminPost, pk=pk)
    comments = post.comments.select_related('author').all()
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            c = comment_form.save(commit=False)
            c.post = post
            c.author = request.user
            c.save()
            return redirect('noticeboard_detail', pk=pk)

    return render(request, 'noticeboard/detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })


@staff_required
def create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, '게시글이 작성되었습니다.')
            return redirect('noticeboard_index')
    else:
        form = PostForm()

    return render(request, 'noticeboard/create.html', {'form': form})
