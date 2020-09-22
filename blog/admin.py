from django.contrib import admin

from .models import UserProfile
from .models import Blog
from .models import Post
from .models import Comment
from .models import Image
from .models import File

admin.site.register(UserProfile)
admin.site.register(Blog)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Image)
admin.site.register(File)
