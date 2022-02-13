from django.contrib import admin
from .models import Post, Comment

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
    'title', 'author', 'image_url', 'visited_places', 'visited_date', 'favorite_place', 'address',
    'favorite_activity', 'description', 'publish')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created')
    list_filter = ('created', 'updated')
    search_fields = ('name', 'email', 'body')


