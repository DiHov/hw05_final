from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from yatube.settings import PAGINATOR

from .forms import CommentForm, PostForm
from .models import Group, Post, Follow

User = get_user_model()


# @cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('index')

    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=author, user=request.user).exists()
    else:
        following = False
    paginator = Paginator(posts, PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'profile.html',
        {'author': author, 'page': page, 'following': following}
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = post.comments.all()
    form = CommentForm()
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author__username=post.author,
            user=request.user).exists()
    else:
        following = False
    paginator = Paginator(comments, 4)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'view_post.html',
        {
            'author': post.author,
            'post': post,
            'page': page,
            'comments': comments,
            'form': form,
            'following': following
        }
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if post.author != request.user:
        return redirect('post', username, post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)
    return render(request, 'new_post.html', {'form': form, 'post': post})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user == post.author:
        return redirect('post', username, post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post', username, post_id)

    # return render(request, 'view_post.html', {'form': form})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page})


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if request.user == author:
        return redirect('profile', username)
    if not Follow.objects.filter(user=request.user, author=author).exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    if follow.exists():
        follow.delete()
    return redirect('profile', username)
