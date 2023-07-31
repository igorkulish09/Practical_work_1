from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import PostForm, CommentForm


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('/home/')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('/home/')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('/login/')


def home(request):
    return render(request, 'accounts/home.html')


def home(request):
    return render(request, 'accounts/home.html')


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if 'publish' in request.POST:
                post.is_published = True
                post.is_draft = False
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'accounts/create_post.html', {'form': form})


def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Перевірка, чи користувач є власником поста
    if post.author != request.user:
        return render(request, 'accounts/access_denied.html')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if 'publish' in request.POST:
                post.is_published = True
                post.is_draft = False
            post.save()
            return redirect('home')
    else:
        form = PostForm(instance=post)
    return render(request, 'accounts/edit_post.html', {'form': form, 'post': post})


def draft_posts(request):
    drafts = Post.objects.filter(author=request.user, is_draft=True)
    return render(request, 'accounts/draft_posts.html', {'drafts': drafts})


def create_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post

            # Перевірка, чи користувач є зареєстрованим
            if request.user.is_authenticated:
                comment.author = request.user
            else:
                comment.author = None

            comment.save()
            return redirect('post_detail', pk=pk)
    else:
        form = CommentForm()
    return render(request, 'accounts/create_comment.html', {'form': form})


def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            if request.user.is_authenticated:
                comment.author = request.user
            comment.save()
            return redirect('post_detail', post_id=post_id)
    else:
        form = CommentForm()

    return render(request, 'accounts/add_comment.html', {'form': form})
