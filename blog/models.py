from django.db import models
from django.urls import reverse
from django.http import Http404
from django.contrib.auth.models import User



class UserProfile(models.Model):
    user   = models.OneToOneField(User, on_delete=models.CASCADE)
    image  = models.ImageField(upload_to='media/user/')

    def __str__(self):
        return str(self.user.username)


class Blog(models.Model):
    name  = models.CharField(max_length=255)
    user  = models.ForeignKey(User, models.CASCADE, related_name="blogs")
    subscribers = models.ManyToManyField(User, related_name="subscriptions", blank=True)

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'blog_id': self.id})

    def get_blog_by_id(self, blog_id):
        try:
            blog = Blog.objects.get(pk=blog_id)
        except self.DoesNotExist:
            raise Http404("Blog with id '" + str(blog_id) + "' does not exist")
        return blog

    def get_blog_list(self, count, offset):
        blog_list = list(Blog.objects.all().order_by('-pub_date')[offset-count:offset])
        if not blog_list:
            raise Http404("Page does not exist")
        return blog_list


class Post(models.Model):
    title      = models.CharField(max_length=255)
    text       = models.TextField(blank=True)
    pub_date   = models.DateTimeField(verbose_name="Date published")
    blog       = models.ForeignKey(Blog, models.CASCADE, related_name="posts")
    user       = models.ForeignKey(User, models.CASCADE, related_name="posts")
    like_count = models.IntegerField("Count of likes", default=0, editable=False)
    liked_by   = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return "/post/" + str(self.pk)

    def get_post_by_id(self, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except self.DoesNotExist:
            raise Http404("Post with id '" + str(post_id) + "' does not exist")
        return post

    def get_post_list(self, count, offset):
        post_list = list(Post.objects.all().order_by('-pub_date')[offset-count:offset])
        if not post_list:
            raise Http404("Page does not exist")
        return post_list


class Comment(models.Model):
    text     = models.TextField()
    pub_date = models.DateTimeField(verbose_name="Date published")
    post     = models.ForeignKey(Post, models.CASCADE, related_name="comments")
    user     = models.ForeignKey(User, models.CASCADE, related_name="comments")

    def __str__(self):
        return str(self.user.username) + ' ' + str(self.pub_date)

    def get_absolute_url(self):
        return self.post.get_absolute_url() + '#comment_' + str(self.id)


class Image(models.Model):
    image_field = models.ImageField(upload_to='media/images')
    post        = models.ManyToManyField(Post, blank=True, related_name="images")
    comment     = models.ManyToManyField(Comment, blank=True, related_name="images")

    def __str__(self):
        return str(self.image_field.name)


class File(models.Model):
    file_field = models.FileField(upload_to='media/files')
    post       = models.ManyToManyField(Post, blank=True, related_name="files")
    comment    = models.ManyToManyField(Comment, blank=True, related_name="files")

    def __str_(self):
        return str(self.file_field.name)
