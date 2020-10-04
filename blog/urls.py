from django.urls import path, include
from django.views.generic import RedirectView
from blog import views

urlpatterns = [
    path('', RedirectView.as_view(url='home/', permanent=True)),
    
    path('home/', views.HomeView.as_view(), name="home"),

    path('me/', views.MyAccountView.as_view(), name="my_account"),

    path('me/edit_profile/', views.MyAccountEditView.as_view(), name="my_account_edit"),

    path('me/blogs/', views.MyBlogsView.as_view(), name="my_blogs"),

    path('me/posts/', views.MyPostsView.as_view(), name="my_posts"),

    path('me/subscriptions/', views.MySubsriptionsView.as_view(), name="subscriptions"),

    path('new_blog/', views.BlogNewView.as_view(), name="blog_new"),
    
    path('new_post/', views.BlogAddPostView.as_view(), name="select_blog_to_add_post"),

    path('news/', views.PostListView.as_view(), name="post_list"),

    path('news/page-<int:page>/', views.PostListView.as_view(), name="post_list_page"),

    path('blogs/', views.BlogListView.as_view(), name="blog_list"),

    path('blogs/page-<int:page>/', views.BlogListView.as_view(), name="blog_list_page"),

    path('post/<int:post_id>/', views.PostDetailView.as_view(), name="post_detail"),

    path('post/<int:post_id>/edit/', views.PostEditView.as_view(), name="post_edit"),

    path('post/<int:post_id>/delete/', views.PostDeleteView.as_view(), name="post_delete"),

    path('blog/<int:blog_id>/', views.BlogDetailView.as_view(), name="blog_detail"),

    path('blog/<int:blog_id>/new_post/', views.PostNewView.as_view(), name="post_new"),

    path('blog/<int:blog_id>/delete', views.BlogDeleteView.as_view(), name="blog_delete"),

    path('blog/<int:blog_id>/page-<int:page>/', views.BlogDetailView.as_view(), name="blog_detail_page"),

    path('users/', views.UserListView.as_view(), name="user_list"),

    path('user/<int:user_id>/', views.UserDetailView.as_view(), name="user_detail"),

    path('login/', views.LogInView.as_view(), name="log_in"),

    path('logout/', views.LogOutView.as_view(), name="log_out"),

    path('sign_up/', views.SignUpView.as_view(), name="sign_up"),
]
