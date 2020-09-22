from django.urls import path, include
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='home/', permanent=True)),
    
    path('home/', views.home, name="home"),

    path('me/', views.my_account, name="my_account"),

    path('me/blogs/', views.my_blogs, name="my_blogs"),

    path('me/posts/', views.my_posts, name="my_posts"),

    path('subscriptions/', views.subscriptions, name="subscriptions"),

    path('new_blog/', views.blog_new, name="blog_new"),
    
    path('new_post/', views.select_blog_to_add_post, name="select_blog_to_add_post"),

    path('news/', views.post_list, name="post_list"),

    path('news/page-<int:page>/', views.post_list, name="post_list_page"),

    path('blogs/', views.blog_list, name="blog_list"),

    path('blogs/page-<int:page>/', views.blog_list, name="blog_list_page"),

    path('post/<int:post_id>/', views.post_detail, name="post_detail"),

    path('post/<int:post_id>/edit/', views.post_edit, name="post_edit"),

    path('post/<int:post_id>/delete/', views.post_delete, name="post_delete"),

    path('blog/<int:blog_id>/', views.blog_detail, name="blog_detail"),

    path('blog/<int:blog_id>/new_post/', views.post_new, name="post_new"),

    path('blog/<int:blog_id>/delete', views.blog_delete, name="blog_delete"),

    path('blog/<int:blog_id>/page-<int:page>/', views.blog_detail, name="blog_detail_page"),

    path('users/', views.user_list, name="user_list"),

    path('user/<int:user_id>/', views.user_detail, name="user_detail"),

    path('login/', views.log_in, name="log_in"),

    path('logout/', views.log_out, name="log_out"),
]
