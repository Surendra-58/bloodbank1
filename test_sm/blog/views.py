

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import BlogPost, BlogLike, BlogComment
from myapp.models import CustomUser
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import BlogPost
from django.contrib import messages
from django.db.models import Prefetch


from django.db.models import Prefetch

@login_required
def blog_feed(request):
    # Prefetch only the latest 10 comments per post, ordered newest-first
    comments_prefetch = Prefetch(
        'comments',
        queryset=BlogComment.objects.select_related('user').order_by('-commented_at')[:10],
        to_attr='latest_comments'
    )

    posts = BlogPost.objects.select_related('author', 'shared_post').prefetch_related(
        'likes',
        comments_prefetch
    )

    for post in posts:
        post.is_liked = post.likes.filter(user=request.user).exists()

    template_map = {
        "1": 'admin/home.html',
        "2": 'hospital/home.html',
        "3": 'donor/home.html'
    }
    return render(request, template_map.get(request.user.user_type, 'login'), {'posts': posts})



@login_required
def create_post(request):
    if request.method == "POST":
        caption = request.POST.get('caption')
        image = request.FILES.get('image')
        
        if not caption:
            messages.error(request, "Caption is required!")
            return redirect('blog:create_post')

        # Create the new post
        BlogPost.objects.create(
            author=request.user,
            caption=caption,
            image=image
        )

        messages.success(request, "Post created successfully!")
        return redirect('blog:blog_feed')

    return render(request, 'blog/create_post.html')




@login_required
def toggle_like(request, post_id):
    post = BlogPost.objects.get(id=post_id)
    like, created = BlogLike.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()  # Unlike if already liked

    return redirect('blog:blog_feed')


@login_required
def comment_on_post(request, post_id):
    post = BlogPost.objects.get(id=post_id)

    if request.method == "POST":
        content = request.POST.get('content')
        parent_comment = request.POST.get('parent_comment')

        comment = BlogComment.objects.create(
            post=post,
            user=request.user,
            content=content,
            parent_id=parent_comment if parent_comment else None
        )

        messages.success(request, "Comment added successfully!")
        return redirect('blog:blog_feed')

    return redirect('blog:blog_feed')


def user_blog_profile(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    posts = BlogPost.objects.filter(author=user).select_related('author')

    return render(request, 'blog/user_blog_profile.html', {
        'user': user,
        'posts': posts
    })

def post_detail(request, post_id):
    post = BlogPost.objects.get(id=post_id)
    comments = BlogComment.objects.filter(post=post).order_by('commented_at')

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments
    })

@login_required
def share_post(request, post_id):
    original_post = BlogPost.objects.get(id=post_id)
    
    if request.method == "POST":
        caption = request.POST.get('caption')
        
        # Create the new post as a shared post
        BlogPost.objects.create(
            author=request.user,
            caption=caption,
            shared_post=original_post
        )
        
        messages.success(request, "Post shared successfully!")
        return redirect('blog:blog_feed')

    return render(request, 'blog/share_post.html', {
        'original_post': original_post
    })