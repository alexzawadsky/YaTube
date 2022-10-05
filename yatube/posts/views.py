from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from yatube.settings import NUMBER_VISIBLE_LINES_IN_POSTCARD

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import paginator


def index(request):
    template = 'posts/index.html'

    posts = Post.objects.all()

    page_obj = paginator(request, posts)

    context = {
        'visible_lines': NUMBER_VISIBLE_LINES_IN_POSTCARD,
        'page_obj': page_obj,
    }
    return render(request, template, context=context)


def group_posts(request, slug):
    template = 'posts/group_list.html'

    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)

    page_obj = paginator(request, posts)

    context = {
        'visible_lines': NUMBER_VISIBLE_LINES_IN_POSTCARD,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context=context)


def profile(request, username):
    template = 'posts/profile.html'
    following = False
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginator(request, posts)
    count = posts.count()
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()

    context = {
        'visible_lines': NUMBER_VISIBLE_LINES_IN_POSTCARD,
        'following': following,
        'count': count,
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post.id)
    count = Post.objects.filter(author=post.author.id).count()
    form = CommentForm()
    context = {
        'form': form,
        'count': count,
        'post': post,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    context = {
        'form': None,
        'is_edit': False,
    }

    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(False)
        post.author_id = request.user.id
        post.save()

        return redirect('posts:profile', request.user.username)

    context['form'] = form
    return render(request, 'posts/create_post.html', context=context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user.id != post.author.id:
        return redirect('posts:post_detail', post.id)

    context = {
        'id': post.id,
        'text': post.text,
        'group': None,
        'is_edit': True,
        'form': None,
    }
    if post.group:
        context['group'] = post.group.title

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)

    if form.is_valid():
        post.save()

        return redirect('posts:post_detail', post.id)

    context['form'] = form
    return render(request, 'posts/create_post.html', context=context)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user.id != post.author.id:
        return redirect('posts:post_detail', post_id)
    post.delete()
    return redirect('posts:profile', request.user.username)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id, post=post)
    if request.user.id == comment.author.id:
        comment.delete()
    return redirect('posts:post_detail', post_id)


def groups(request):
    template = 'posts/groups.html'
    groups = Group.objects.all()
    page_obj = paginator(request, groups)

    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context=context)


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(
        author__following__user=request.user
    )
    posts_exist = posts_list.exists()
    page_obj = paginator(request, posts_list)
    context = {
        'visible_lines': NUMBER_VISIBLE_LINES_IN_POSTCARD,
        'posts_exist': posts_exist,
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.id == author.id:
        return redirect('posts:profile', username=username)
    if Follow.objects.filter(user=request.user, author=author).exists():
        return redirect('posts:profile', username=username)
    Follow.objects.create(
        user=request.user,
        author=author
    )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.id == author.id:
        return redirect('posts:profile', username=username)
    if not Follow.objects.filter(user=request.user, author=author).exists():
        return redirect('posts:profile', username=username)
    follow = get_object_or_404(
        Follow,
        user=request.user,
        author=author
    )
    follow.delete()
    return redirect('posts:profile', username=username)
