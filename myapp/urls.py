from myapp import views
from django.contrib.auth import views as auth_views
from django.urls import path, include
from .views import UserConfirmEmailView, UserConfirmedView, UserConfirmationFailedView, UserUpdateView, reset_password, \
    UserResetDoneView, UserListView, toggle_users_activity, index, send_mailing_now


app_name = 'myapp'

urlpatterns = [
    path('', index, name='index'),
    path('', views.MailingList.as_view(), name='home'),

    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/update/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clients/', views.ClientList.as_view(), name='client_list'),
    path('clients/<int:pk>/', views.ClientDetail.as_view(), name='client_detail'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),

    path('mailings/', views.MailingList.as_view(), name='mailing_list'),
    path('mailings/<int:pk>/', views.MailingDetailPage.as_view(), name='mailing_detail'),
    path('mailings/create/', views.CreateMailing.as_view(), name='create_mailing'),
    path('send_mailing_now/<int:pk>/', views.send_mailing_now, name='send_mailing_now'),
    path('mailings/<int:pk>/edit/', views.EditMailing.as_view(), name='edit_mailing'),
    path('mailings/<int:pk>/delete/', views.DeleteMailing.as_view(), name='delete_mailing'),
    path('create_mailing_log/<int:mailing_id>/', views.CreateMailingLog.as_view(), name='create_mailing_log'),

    path('create_message/', views.CreateMessage.as_view(), name='create_message'),
    path('messages/<int:pk>/edit/', views.EditMessage.as_view(), name='edit_message'),
    path('messages/<int:pk>/delete/', views.DeleteMessage.as_view(), name='delete_message'),

    path('logs/', views.LogList.as_view(), name='log_list'),
    path('logs/<int:pk>/', views.LogDetail.as_view(), name='log_detail'),

    path('accounts/', include('allauth.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('register/', views.RegisterView.as_view(template_name='registration/register.html'), name='register'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('signup/', views.signup, name='signup'),

    path('blog/', include('blog.urls')),

    path('confirm_email/<str:uidb64>/<str:token>/', UserConfirmEmailView.as_view(), name='confirm_email'),
    path('email_confirmed/', UserConfirmedView.as_view(), name='email_confirmed'),
    path('email_confirmation_failed/', UserConfirmationFailedView.as_view(), name='email_confirmation_failed'),
    path('profile/', UserUpdateView.as_view(), name='profile'),
    path('user/list/', UserListView.as_view(), name='user_list'),

    path('password_reset/', reset_password, name='password_reset'),
    path('password_reset/done/', UserResetDoneView.as_view(), name='password_reset_done'),
    path('toggle_users_activity/<int:pk>', toggle_users_activity, name='toggle_users_activity'),
]

