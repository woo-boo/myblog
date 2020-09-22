from django import forms
from django.contrib.auth.models import User
from .models import Post, Blog, Comment



class PostForm(forms.ModelForm):
    class Meta:
        model  = Post
        fields = ['title', 'text', ]



class DeletePostForm(forms.ModelForm):
    class Meta:
        model  = Post
        fields = []



class BlogForm(forms.ModelForm):
    class Meta:
        model  = Blog
        fields = ['name', ]



class DeleteBlogForm(forms.ModelForm):
    class Meta:
        model  = Blog
        fields = []



class UserForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name']



class DeleteUserForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = []



class CommentForm(forms.ModelForm):
    class Meta:
        model  = Comment
        fields = ['text',]



class DeleteCommentForm(forms.ModelForm):
    class Meta:
        model  = Comment
        fields = []



class LoginForm(forms.Form):
    username = forms.CharField(label="Your username", max_length=100, required=True)
    password = forms.CharField(label="Your password", max_length=100, required=True)


