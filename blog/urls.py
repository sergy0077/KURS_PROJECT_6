from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('blog_list/', views.BlogPostListView.as_view(), name='blog_list'),
    path('create/', views.BlogPostCreateView.as_view(), name='create'),
    path('edit/<int:pk>', views.BlogPostUpdateView.as_view(), name='edit'),
    path('view/<int:pk>/', views.BlogPostDetailView.as_view(), name='view'),
    path('blog_delete/<int:pk>', views.BlogPostDeleteView.as_view(), name='blog_delete'),
]
