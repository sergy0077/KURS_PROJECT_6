from django.contrib import admin
from blog.models import BlogPost


@admin.register(BlogPost)  # Регистрация модели блога в административной панели
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'creation_date', 'views_count')
