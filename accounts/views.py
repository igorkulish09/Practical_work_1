from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .forms import ContactForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_page
from .tasks import send_email


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


def all_posts(request):
    posts = Post.objects.all()
    return render(request, 'accounts/all_posts.html', {'posts': posts})


@login_required
def user_posts(request):
    user = request.user
    posts = Post.objects.filter(author=user)
    return render(request, 'accounts/user_posts.html', {'posts': posts})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'accounts/post_detail.html', {'post': post})


class PostListView(ListView):
    model = Post
    template_name = 'accounts/all_posts.html'
    context_object_name = 'posts'


class PostDetailView(DetailView):
    model = Post
    template_name = 'accounts/post_detail.html'
    context_object_name = 'post'


class UserPostsView(ListView):
    model = Post
    template_name = 'accounts/user_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        user = User.objects.get(pk=self.kwargs['pk'])
        return Post.objects.filter(author=user)


def user_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/user_profile.html', {'user': user})


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            subject = f"New Contact Form Submission from {name}"
            mail_message = f"From: {name}\nEmail: {email}\n\n{message}"
            send_mail(subject, mail_message, 'your_email@example.com', ['admin@example.com'])
    else:
        form = ContactForm()
    return render(request, 'accounts/contact.html', {'form': form})


def post_list(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)  # Показувати 10 постів на сторінці

    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'accounts/post_list.html', {'posts': posts})


def comment_list(request, post_id):
    post = Post.objects.get(id=post_id)
    comments = Comment.objects.filter(post=post)
    paginator = Paginator(comments, 10)  # Показувати 10 коментарів на сторінці

    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)

    return render(request, 'accounts/comment_list.html', {'post': post, 'comments': comments})


@cache_page(60 * 15)
def my_view(request):
    send_email.delay('Subject', 'Message', 'from@example.com', ['to@example.com'])
