from django import forms
from blog.models import BlogPost
from myapp.forms import StyleFormMixin


class BlogPostForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ('title', 'content', 'preview', 'creation_date')

