from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView
from blog.forms import BlogPostForm
from blog.models import BlogPost
from blog.services import get_BlogPost_cache


class BlogPostCreateView(PermissionRequiredMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    permission_required = 'blog.add_article'
    success_url = '/blog_list/'
    template_name = 'blog/blog_form.html'


class BlogPostUpdateView(PermissionRequiredMixin, UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    permission_required = 'blog.change_article'
    template_name = 'blog/blog_form.html'

    def get_success_url(self):
        return reverse('blog:view', args=[self.kwargs.get('pk')])


class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog/blog_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'object_list': get_BlogPost_cache()
        }
        return context


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blog_detail.html'

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.object.views_count += 1
        self.object.save()
        return self.object


class BlogPostDeleteView(PermissionRequiredMixin, DeleteView):
    model = BlogPost
    permission_required = 'blog.delete_article'
    success_url = '/blog_list/'
    template_name = 'blog/blog_confirm_delete.html'

