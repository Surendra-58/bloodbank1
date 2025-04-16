

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
    # Get the user_type filter from the URL query parameters
    user_type_filter = request.GET.get('user_type', None)

    # If no filter is provided, use the current user's user_type
    if user_type_filter is None:
        user_type_filter = request.user.user_type

    # Filter posts based on the selected user_type
    if user_type_filter == "1":  # Admin
        posts = BlogPost.objects.filter(author__user_type="1").select_related('author', 'shared_post').prefetch_related('likes', 'comments')
    elif user_type_filter == "2":  # Hospital
        posts = BlogPost.objects.filter(author__user_type="2").select_related('author', 'shared_post').prefetch_related('likes', 'comments')
    elif user_type_filter == "3":  # Donor
        posts = BlogPost.objects.filter(author__user_type="3").select_related('author', 'shared_post').prefetch_related('likes', 'comments')
    else:
        return redirect("login")

    # Add 'is_liked' status to each post
    for post in posts:
        post.is_liked = post.likes.filter(user=request.user).exists()

    # Return the appropriate template based on the user's user_type
    if request.user.user_type == "1":  # Admin
        return render(request, 'admin/home.html', {'posts': posts, 'user_type_filter': user_type_filter})
    elif request.user.user_type == "2":  # Hospital
        return render(request, 'hospital/home.html', {'posts': posts, 'user_type_filter': user_type_filter})
    elif request.user.user_type == "3":  # Donor
        return render(request, 'donor/home.html', {'posts': posts, 'user_type_filter': user_type_filter})
    else:
        return redirect("login")

# @login_required
# def blog_feed(request):
#     # Fetch all posts, and filter by user type in the template
#     posts = BlogPost.objects.select_related('author', 'shared_post').prefetch_related('likes', 'comments')

#     for post in posts:
#         post.is_liked = post.likes.filter(user=request.user).exists()

#     return render(request, 'blog/blog_feed.html', {'posts': posts})



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
        
        # Redirect back to the post detail page
        return HttpResponseRedirect(reverse('blog:post_detail', args=[post_id]))

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