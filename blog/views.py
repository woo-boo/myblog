from django.views import View
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth import logout as django_logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from blog.models import Blog, Post, Comment
from blog.forms  import *


class HomeView(View):

    def get(self, request):
        datetime_now = timezone.now()
        timerange    = [datetime_now - timezone.timedelta(1), datetime_now]
        post_list = Post.objects.filter(pub_date__range=timerange).order_by('-like_count')[:5]
        blog_list = Blog.objects.all().order_by('-id')[:5]

        context = {
            'post_list': post_list,
            'blog_list': blog_list,
            'time': datetime_now,
        }
        return render(request, 'blog/home.html', context)


class PostDetailView(View):

    def get(self, request, post_id):
        post = Post().get_post_by_id(post_id)
        comment_list = post.comments.all().order_by('-pub_date')

        form_add_comment = CommentForm()
        form_delete_comment = DeleteCommentForm()

        try:
            if post.liked_by.get(pk=request.user.id):
                liked = True
        except User.DoesNotExist:
            liked = False

        context = {
            'post': post,
            'liked': liked,
            'comment_list': comment_list,
            'form_add_comment': form_add_comment,
            'form_delete_comment': form_delete_comment,
        }
        return render(request, 'blog/post/post_detail.html', context)
    
    @method_decorator(login_required)
    def post(self, request, post_id):
        form_add_comment = CommentForm(request.POST)
        user = request.user
        post = Post().get_post_by_id(post_id)

        if form_add_comment.is_valid():
            new_comment = form_add_comment.save(commit=False)
            new_comment.user = request.user
            new_comment.post = post
            new_comment.pub_date = timezone.now()
            new_comment.save()
            return HttpResponseRedirect(post.get_absolute_url() + '#comments')
        
        if request.POST.get('comment_id'):
            comment_id = request.POST.get('comment_id')
            comment = Comment.objects.get(pk=comment_id)
            if request.user == comment.user:
                comment.delete()
                return HttpResponseRedirect(post.get_absolute_url() + '#comments')

        if request.POST.get('like_post'):
            try:
                user_liked_by = post.liked_by.get(pk=user.id)
                post.liked_by.remove(user_liked_by)
                post.like_count -= 1
                post.save()
            except User.DoesNotExist:
                post.liked_by.add(user)
                post.like_count += 1
                post.save()
            return HttpResponseRedirect(post.get_absolute_url())


class BlogDetailView(View):

    def get(self, request, blog_id, page=1):
        posts_per_page = 10

        blog = Blog().get_blog_by_id(blog_id)
        post_list_raw = blog.posts.all().order_by('-pub_date')

        paginator = Paginator(post_list_raw, posts_per_page)
        post_list = paginator.get_page(page)

        if request.user.is_authenticated:
            try:
                if blog.subscribers.get(pk=request.user.id):
                    subscribed = True
            except User.DoesNotExist:
                subscribed = False
        else:
            subscribed = False

        context = {
            'blog': blog, 
            'post_list': post_list,
            'pagination': post_list,
            'pagination_url': '/blog/' + str(blog_id) + '/page-',
            'subscribed': subscribed,        
        }
        return render(request, 'blog/blog/blog_detail.html', context)


class BlogNewView(View):

    @method_decorator(login_required)
    def get(self, request):
        form = BlogForm()
        context = {
            'form': form,
        }
        return render(request, 'blog/blog/blog_new.html', context)

    @method_decorator(login_required)
    def post(self, request):
        form = BlogForm(request.POST)
        if form.is_valid():
            new_blog = form.save(commit=False)
            new_blog.user = request.user
            new_blog.save()
            return HttpResponseRedirect(reverse('my_blogs'))


class BlogDeleteView(View):

    @method_decorator(login_required)
    def get(self, request, blog_id):
        form = DeleteBlogForm()
        blog = Blog().get_blog_by_id(blog_id)
        context = {
            'form': form,
            'blog': blog,
        }
        return render(request, 'blog/blog/blog_delete.html', context)

    @method_decorator(login_required)
    def post(self, request, blog_id):
        form = DeleteBlogForm(request.POST)
        blog = Blog().get_blog_by_id(blog_id)
        if form.is_valid():
            blog.delete()
            return render(request, 'blog/messages/blog_was_deleted.html')


class BlogAddPostView(View):

    @method_decorator(login_required)
    def get(self, request):
        blog_list = Blog.objects.filter(user=request.user).order_by('-id')
        context = {
            'blog_list': blog_list,
        }
        return render(request, 'blog/blog/blog_add_post.html', context)


class PostNewView(View):

    @method_decorator(login_required)
    def get(self, request, blog_id):
        blog = Blog().get_blog_by_id(blog_id)

        if request.user != blog.user:
            return render(request, 'blog/message/no_permissions.html')

        form = PostForm()
        context = {
            'form': form,
            'blog': blog,
        }
        return render(request, 'blog/post/post_new.html', context)

    @method_decorator(login_required)
    def post(self, request, blog_id):
        blog = Blog().get_blog_by_id(blog_id)
        form = PostForm(request.POST)

        if request.user == blog.user:
            if form.is_valid():
                new_post = form.save(commit=False)
                new_post.user = blog.user
                new_post.pub_date = timezone.now()
                new_post.blog = blog
                new_post.save()
                return HttpResponseRedirect(blog.get_absolute_url())


class PostEditView(View):

    @method_decorator(login_required)
    def get(self, request, post_id):
        post = Post().get_post_by_id(post_id)

        if request.user != post.user:
            return render(request, 'blog/messages/no_permissions.html')
        
        form = PostForm(instance=post)
        context = {
            'form': form,
            'post': post,
        }
        return render(request, 'blog/post/post_edit.html', context)

    def post(self, request, post_id):
        post = Post().get_post_by_id(post_id)

        if request.user == post.user:
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                edited_post = form.save(commit=False)
                edited_post.save()
                return HttpResponseRedirect(post.get_absolute_url())


class PostDeleteView(View):

    @method_decorator(login_required)
    def get(self, request, post_id):
        post = Post().get_post_by_id(post_id)

        if request.user != post.user:
            return render(request, 'blog/messages/no_permissions.html')
        
        form = DeletePostForm()
        context = {
            'form': form,
            'post': post,
        }
        return render(request, 'blog/post/post_delete.html', context)

    def post(self, request, post_id):
        post = Post().get_post_by_id(post_id)

        if request.user == post.user:
            form = DeletePostForm(request.POST)
            if form.is_valid():
                post.delete()
                return render(request, 'blog/messages/post_was_deleted.html')


class MyAccountView(View):

    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        blog_list = user.blogs.all()
        context = {
            'user_detail': user,
            'blog_list': blog_list,
        }
        return render(request, 'blog/user/my_account.html', context)


class MyAccountEditView(View):

    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        form = UserForm(instance=user)
        context = {
            'user_detail': user,
            'form': form,
        }
        return render(request, 'blog/user/user_edit.html', context)

    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            edited_user = form.save()
            return HttpResponseRedirect(reverse('my_account'))


class MyBlogsView(View):

    @method_decorator(login_required)
    def get(self, request):
        blog_list = Blog.objects.filter(user=request.user).order_by('-id')
        context = {
            'blog_list': blog_list,
        }
        return render(request, 'blog/user/my_blogs.html', context)


class MyPostsView(View):

    @method_decorator(login_required)
    def get(self, request):
        post_list = Post.objects.filter(user=request.user).order_by('-id')
        context = {
            'post_list': post_list,
        }
        return render(request, 'blog/post/post_list.html', context)


class MySubsriptionsView(View):

    @method_decorator(login_required)
    def get(self, request):
        blog_list = request.user.subscriptions.all().order_by('-id')
        context = {
            'blog_list': blog_list,
        }
        return render(request, 'blog/user/my_subscriptions.html', context)
    
    @method_decorator(login_required)
    def post(self, request):
        blog_id = request.POST.get('subscribe_to_blog_id')
        blog = Blog.objects.get(pk=blog_id)
        user = request.user
        try:
            subscriber = blog.subscribers.get(pk=user.id)
            blog.subscribers.remove(subscriber)
        except User.DoesNotExist:
            blog.subscribers.add(user)
        return HttpResponseRedirect(blog.get_absolute_url())


class PostListView(View):

    def get(self, request, page=1):
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


class BlogListView(View):

    def get(self, request, page=1):
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


class UserListView(View):

    def get(self, request):
        user_list = User.objects.all().order_by('-date_joined')
        context = {
            'user_list': user_list,
        }
        return render(request, 'blog/user/user_list.html', context)


class UserDetailView(View):

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)

        if user == request.user:
            return HttpResponseRedirect(reverse('my_account'))

        blog_list = user.blogs.all().order_by('-id')

        context = {
            'user_detail': user,
            'blog_list': blog_list,
        }

        return render(request, 'blog/user/user_detail.html', context)


class LogInView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('my_account'))
        form = LoginForm()
        context = {
            'form': form,
        }
        return render(request, 'blog/registration/log_in.html', context)

    def post(self, request):
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

        context = {
            'form': form,
        }
        return render(request, 'blog/registration/log_in.html', context)


class LogOutView(View):
    
    def get(self, request):
        django_logout(request)
        return HttpResponseRedirect(reverse('log_in'))


class SignUpView(View):
    
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('my_account'))

        form = UserCreationForm()
        context = {
            'form': form,
        }
        return render(request, 'blog/registration/sign_up.html', context)

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid:
            try:
                new_user = form.save(commit=False)
                new_user.first_name = 'New'
                new_user.last_name = 'User'
                form.save()
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect(reverse('my_account_edit'))
            except ValueError:
                context = {
                    'form': form,
                }
                return render(request, 'blog/registration/sign_up.html', context)