from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth import logout as django_logout, login, authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import UserProfile, Blog, Post, Comment, Image, File
from .forms  import PostForm, DeletePostForm, BlogForm, DeleteBlogForm
from .forms  import UserForm, DeleteUserForm, CommentForm, DeleteCommentForm
from .forms  import LoginForm



def home(request):
    datetime_now = timezone.now()
    timerange    = [datetime_now - timezone.timedelta(1), datetime_now]
    post_list = Post.objects.filter(pub_date__range=timerange).order_by('-pub_date')[:5]
    blog_list = Blog.objects.all().order_by('-id')[:5]

    context = {
        'post_list': post_list,
        'blog_list': blog_list,
        'time': datetime_now,
    }

    return render(request, 'blog/home.html', context)



def post_detail(request, post_id):
    post = Post().get_post_by_id(post_id)
    comment_list = post.comments.all().order_by('-pub_date')

    if request.user.is_authenticated:
        if request.method == 'POST':
            form_add_comment = CommentForm(request.POST)
            form_delete_comment = DeleteCommentForm(request.POST)

            if form_add_comment.is_valid():
                new_comment = form_add_comment.save(commit=False)
                new_comment.user = request.user
                new_comment.post = post
                new_comment.pub_date = timezone.now()
                new_comment.save()
                return HttpResponseRedirect(post.get_absolute_url() + '#comments')

            if form_delete_comment.is_valid():
                comment_id = request.POST.get('comment_id')
                Comment.objects.get(pk=comment_id).delete()
                return HttpResponseRedirect(post.get_absolute_url() + '#comments')

        else:
            form_add_comment = CommentForm()
            form_delete_comment = DeleteCommentForm

    context = {
        'post': post,
        'comment_list': comment_list,
        'form_add_comment': form_add_comment,
        'form_delete_comment': form_delete_comment,
    }

    return render(request, 'blog/post/post_detail.html', context)




def blog_detail(request, blog_id, page=1):
    posts_per_page = 10

    blog = Blog().get_blog_by_id(blog_id)
    post_list_raw = blog.posts.all().order_by('-pub_date')

    paginator = Paginator(post_list_raw, posts_per_page)
    post_list = paginator.get_page(page)

    context = {
        'blog': blog, 
        'post_list': post_list,
        'pagination': post_list,
        'pagination_url': '/blog/' + str(blog_id) + '/page-',
    }

    return render(request, 'blog/blog/blog_detail.html', context)



@login_required
def blog_new(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            new_blog = form.save(commit=False)
            new_blog.user = request.user
            new_blog.save()
            return HttpResponseRedirect(reverse('my_blogs'))
    else:
        form = BlogForm()

        context = {
            'form': form,
        }

        return render(request, 'blog/blog/blog_new.html', context)



@login_required
def blog_delete(request, blog_id):
    blog = Blog().get_blog_by_id(blog_id)
    if request.method == 'POST':
        form = DeleteBlogForm(request.POST)
        if form.is_valid():
            blog.delete()
            return render(request, 'blog/messages/blog_was_deleted.html')
    else:
        form = DeleteBlogForm()
        
        context = {
            'form': form,
            'blog': blog,
        }

        return render(request, 'blog/blog/blog_delete.html', context)


@login_required
def select_blog_to_add_post(request):
    blog_list = Blog.objects.filter(user=request.user).order_by('-id')

    context = {
        'blog_list': blog_list,
    }

    return render(request, 'blog/post/select_blog_to_add_post.html', context)


@login_required
def post_new(request, blog_id):
    blog = Blog().get_blog_by_id(blog_id)
    
    if request.user is not blog.user:
        return render(request, 'blog/messages/no_permissions.html')

    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = blog.user
            new_post.pub_date = timezone.now()
            new_post.blog = blog
            new_post.save()
            return HttpResponseRedirect(blog.get_absolute_url())
    else:
        form = PostForm()

        context = {
            'form': form,
            'blog': blog,
        }  
     
        return render(request, 'blog/post/post_new.html', context)



@login_required
def post_edit(request, post_id):
    post = Post().get_post_by_id(post_id)

    if request.user is not post.user:
        return render(request, 'blog/messages/no_permissions.html')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            edited_post = form.save(commit=False)
            edited_post.save()
            return HttpResponseRedirect(post.get_absolute_url())
    else:
        form = PostForm(instance=post)
    
        context = {
            'form': form,
            'post': post,
        }

        return render(request, 'blog/post/post_edit.html', context)



@login_required
def post_delete(request, post_id):
    post = Post().get_post_by_id(post_id)
        
    if request.user is not post.user:
        return render(request, 'blog/messages/no_permissions.html')

    if request.method == 'POST':
        form = DeletePostForm(request.POST)
        if form.is_valid():
            post.delete()
            return render(request, 'blog/messages/post_was_deleted.html')
    else:
        form = DeletePostForm()

        context = {
            'form': form,
            'post': post,
        }

        return render(request, 'blog/post/post_delete.html', context)



@login_required
def my_account(request):
    user = request.user
    blog_list = user.blogs.all()

    context = {
        'user': user,
        'blog_list': blog_list,
    }

    return render(request, 'blog/user/my_account.html', context)



@login_required
def my_account_edit(request):
    user = request.user
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            edited_user = form.save()
            return HttpResponseRedirect(user.get_absolute_url())
    else:
        form = PostForm(instance=user)

        context = {
            'form': form,
        }
        
        return render(request, 'blog/user/user_edit.html', context)



@login_required
def my_blogs(request):
    blog_list = Blog.objects.filter(user=request.user).order_by('-id')

    context = {
        'blog_list': blog_list,
    }

    return render(request, 'blog/user/my_blogs.html', context)



@login_required
def my_posts(request):
    post_list = Post.objects.filter(user=request.user).order_by('-pub_date')

    context = {
        'post_list': post_list,
    }

    return render(request, 'blog/post/post_list.html', context)



@login_required
def subscriptions(request):
    blog_list = request.user.subscriptions.all().order_by('-id')

    context = {
        'blog_list': blog_list,
    }

    return render(request, 'blog/user/subscriptions.html', context)



def post_list(request, page=1):
    posts_per_page = 10
    post_list_raw = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list_raw, posts_per_page)
    post_list = paginator.get_page(page)

    context = {
        'post_list': post_list,
        'pagination': post_list,
        'pagination_url': '/news/page-',
    }

    return render(request, 'blog/post/post_list.html', context)



def blog_list(request, page=1):
    blogs_per_page = 10
    blog_list_raw = Blog.objects.all().order_by('-id')
    paginator = Paginator(blog_list_raw, blogs_per_page)
    blog_list = paginator.get_page(page)

    context = {
        'blog_list': blog_list,
        'pagination': blog_list,
        'pagination_url': '/blogs/page-',
    }

    return render(request, 'blog/blog/blog_list.html', context)



def user_list(request):
    user_list = User.objects.all().order_by('-date_joined')

    context = {
        'user_list': user_list,
    }

    return render(request, 'blog/user/user_list.html', context)



def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    blog_list = user.blogs.all().order_by('-id')

    context = {
        'user': user,
        'blog_list': blog_list,
    }

    return render(request, 'blog/user/user_detail.html', context)



def log_in(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))
            else:
                form.errors.main = "Wrong login or password"
        else:
            form.errors.main = "Uncorrect data"
    else:
        form = LoginForm()

    context = {
        'form': form,
    }

    return render(request, 'blog/registration/log_in.html', context)



def log_out(request):
    django_logout(request)
    return HttpResponseRedirect(reverse('log_in'))
