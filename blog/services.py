from django.conf import settings
from django.core.cache import cache

from blog.models import BlogPost


def get_BlogPost_cache():
    if settings.CACHE_ENABLED:
        key = 'blog_list'
        blog_list = cache.get(key)
        if blog_list is None:
            category_list = BlogPost.objects.all()
            cache.set(key, category_list)
    else:
        blog_list = BlogPost.objects.all()
    return blog_list