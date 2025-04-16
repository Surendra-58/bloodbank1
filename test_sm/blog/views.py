

from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import BlogPost, BlogLike, BlogComment
from myapp.models import CustomUser
from django.contrib import messages
from django.db.models import Prefetch
from django.urls import reverse

@login_required
def blog_feed(request):
    user_type_filter = request.GET.get('user_type')

    if not user_type_filter:
        user_type_filter = "my_posts"  # default to logged-in user's posts

    if user_type_filter == "my_posts":
        posts = BlogPost.objects.filter(
            author=request.user
        ).select_related('author', 'shared_post').prefetch_related('likes', 'comments')

    elif user_type_filter in ["1", "2", "3"]:
        queryset = BlogPost.objects.filter(
            author__user_type=user_type_filter
        )

        # Exclude current user's posts if not admin
        if request.user.user_type != "1":
            queryset = queryset.exclude(author=request.user)

        posts = queryset.select_related('author', 'shared_post').prefetch_related('likes', 'comments')

    else:
        return redirect("login")

    # Add 'is_liked' flag
    for post in posts:
        post.is_liked = post.likes.filter(user=request.user).exists()

    # Choose template
    template = {
        "1": 'admin/home.html',
        "2": 'hospital/home.html',
        "3": 'donor/home.html'
    }.get(request.user.user_type, 'login')

    return render(request, template, {
        'posts': posts,
        'user_type_filter': user_type_filter
    })





@login_required
def delete_post(request, post_id):
    # Retrieve the post, or return a 404 if not found
    post = get_object_or_404(BlogPost, id=post_id)

    # Ensure the logged-in user is the author
    if post.author == request.user:
        post.delete()  # Delete the post if the user is the author
        
        # Redirect to the home page after deletion
        return redirect(reverse('home'))  # Ensure this matches your URL pattern name for the home page
    else:
        raise Http404("You are not authorized to delete this post.")  # Unauthorized access

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