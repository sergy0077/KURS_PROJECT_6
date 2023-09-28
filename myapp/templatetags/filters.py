from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()


@register.filter(needs_autoescape=True)
def split(text, autoescape=True):
    """Обрезает переданный текст до 100 символов"""
    result = text[0:100]
    return mark_safe(result)


@register.filter
def mediapath_filtr(path):
    """Фильтр, который преобразует переданный путь в полный путь для доступа к медиафайлу"""
    return f"{settings.MEDIA_URL}{path}"


@register.simple_tag
def mediapath_tag(path):
    """Шаблонный тег, который преобразует переданный путь в полный путь для доступа к медиафайлу"""
    return f"{settings.MEDIA_URL}{path}"