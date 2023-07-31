from django.contrib import admin
from .models import CustomUser, Post, Comment


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_date', 'is_published')
    list_filter = ('is_published',)


admin.site.register(CustomUser)
admin.site.register(Post)
admin.site.register(Comment, CommentAdmin)

