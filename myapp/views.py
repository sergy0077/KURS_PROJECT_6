from django.contrib.auth.views import PasswordResetDoneView, RedirectURLMixin
from django.db.models import Q, QuerySet
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from typing import Any
from pytils.translit import slugify
from django.urls import reverse_lazy, reverse
from .models import MailingSettings, MailingLog, Client, Message, User, MailingStatus
from myapp.forms import MailingSettingsForm, ClientForm, MessageForm, UserForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from myapp.services import (
    check_mailing_status, check_user, get_status_object, check_link, send_block_notification,
    send_reset_password_mail
)
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView, TemplateView, FormView
from blog.models import BlogPost
from django.core.exceptions import ObjectDoesNotExist

######################################################################

'''Функция отображения главной страницы сервиса'''

def index(request):
    try:
        mailing_all = MailingSettings.objects.count()
    except ObjectDoesNotExist:
        mailing_all = 0

    try:
        status_name = "запущена"
        status_object = MailingStatus.objects.get(name=status_name)
        mailing_active = MailingSettings.objects.filter(status=status_object).count()
    except ObjectDoesNotExist:
        mailing_active = 0

    clients_count = Client.objects.count()

    last_articles = BlogPost.objects.all().order_by('-id')[:3]

    context_data = {
        'mailing_all': mailing_all,
        'mailing_active': mailing_active,
        'clients_count': clients_count,
        'last_articles': last_articles
    }

    return render(request, 'main_page.html', context=context_data)


#############################################################################

"""Представление для главной страницы"""

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing_count'] = MailingSettings.objects.count()
        context['active_mailing_count'] = MailingSettings.objects.filter(status='started').count()
        context['unique_client_count'] = Client.objects.count()
        context['random_blog_posts'] = BlogPost.objects.order_by('?')[:3]
        return context

#######################################################################

"""Блок пользователей - USER"""


class LoginView(RedirectURLMixin, FormView):
    template_name = 'registration/login.html'


class LogoutView(RedirectURLMixin, FormView):
    template_name = 'registration/logout.html'


class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('myapp:home')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class UserConfirmationSentView(PasswordResetDoneView):
    template_name = "confirmation/registration_sent_done.html"


class UserConfirmEmailView(View):
    def get(self, request, uidb64, token):
        is_success = check_link(request, uidb64, token)
        if is_success:
            return redirect('myapp/confirmation/:email_confirmed')
        else:
            return redirect('myapp/confirmation/:email_confirmation_failed')


class UserConfirmedView(TemplateView):
    template_name = 'confirmation/registration_confirmed.html'


class UserConfirmationFailedView(TemplateView):
    template_name = 'confirmation/email_confirmation_failed.html'


class UserUpdateView(UpdateView):
    model = User
    form_class = UserForm
    success_url = reverse_lazy('myapp:profile')

    def get_object(self, queryset=None):
        return self.request.user


def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        send_reset_password_mail(email)
        return redirect('myapp/confirmation:password_reset_done')
    return render(request, 'confirmation/password_reset_form.html')


class UserResetDoneView(PasswordResetDoneView):
    model = User
    template_name = 'confirmation/password_reset_done.html'



class UserListView(PermissionRequiredMixin, ListView):
    model = User
    template_name = 'user_list.html'
    permission_required = 'myapp.set_active'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(groups__name='Service_user')

        return User.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context['object_list'])
        return context


class UserDeleteView(DeleteView):
    model = User
    success_url = reverse_lazy('myapp: general')


def is_moderator(user):
    return user.groups.filter(name='Moderator').exists()


def is_member(user):
    pass


class MyView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def test_func(self):
        return not is_member(self.request.user)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('mailing_list')
    else:
        form = UserCreationForm()
    return render(request, 'myapp/registration/signup.html', {'form': form})


def toggle_users_activity(request, pk):
    user = User.objects.get(pk=pk)
    if user.is_active:
        user.is_active = False
        send_block_notification(user)
    else:
        user.is_active = True
    user.save()
    return redirect(reverse('myapp:user_list'))


############################################################################

"""Блок клиента"""

class ClientCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'client_create.html'
    success_url = reverse_lazy('myapp:client_list')
    permission_required = 'myapp.add_client'

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('myapp:client_list')


class ClientUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'client_update.html'
    success_url = reverse_lazy('myapp:client_list')
    permission_required = 'myapp.change_client'

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user:
            raise Http404("Вы не являетесь создателем данного клиента, у вас нет прав на его редактирование.")
        return self.object

    def get_success_url(self):
        return reverse('myapp:client_list', args=[self.kwargs.get('pk')])


class ClientDelete(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Client
    template_name = 'client_delete.html'
    success_url = reverse_lazy('myapp:client_list')
    permission_required = 'myapp.delete_client'

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user:
            raise Http404("Вы не являетесь создателем данного клиента, у вас нет прав на его удаление.")
        return self.object

    def get_success_url(self):
        return reverse('myapp:client_list')


class ClientList(LoginRequiredMixin, ListView, PermissionRequiredMixin):
    model = Client
    template_name = 'client_list.html'
    context_object_name = 'object_list'
    permission_required = 'myapp.view_client'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class ClientDetail(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Client
    template_name = 'client_detail.html'
    permission_required = 'myapp.view_client'


##########################################################################

"""Блок сообщений"""
class CreateMessage(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'create_message.html'
    success_url = reverse_lazy('myapp:mailing_list')


class EditMessage(UpdateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'edit_message.html'
    success_url = reverse_lazy('myapp:mailing_list')


class DeleteMessage(DeleteView):
    model = Message
    template_name = 'delete_message.html'
    success_url = reverse_lazy('myapp:mailing_list')


#####################################################################################

"""Блок рассылок"""


class CreateMailing(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = MailingSettings
    form_class = MailingSettingsForm
    template_name = 'create_mailing.html'
    permission_required = 'myapp.add_mail'

    def get_success_url(self):
        return reverse('myapp:mailing_list')

    def form_valid(self, form) -> HttpResponse:
        if form.is_valid():
            self.object = form.save()
            self.object.status = MailingStatus.objects.get(name='создана')
            self.object.slug = slugify(f'{self.object.title}-{self.object.pk}')
            self.object.user = self.request.user
            self.object.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание рассылки'

        return context


class EditMailing(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    '''Класс для редактирования рассылки'''
    model = MailingSettings
    fields = ['title', 'message', 'sending_time', 'regularity', 'status']
    template_name = 'edit_mailing.html'
    success_url = reverse_lazy('myapp:mailing_list')
    permission_required = 'myapp.change_mail'

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        mailing = self.get_object()

        if not check_user(mailing.user, self.request.user) or not check_mailing_status(mailing, 'создана'):
            return redirect('myapp:mailing_list')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form) -> HttpResponse:
        if form.is_valid():
            self.object = form.save()
            self.object.slug = slugify(f'{self.object.title}-{self.object.pk}')
            self.object.save()

        return super().form_valid(form)



class MailingList(LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin, ListView):
    model = MailingSettings
    template_name = 'mailing_list.html'
    context_object_name = 'object_list'
    permission_required = 'myapp.view_mail'

    def get_queryset(self, *args, **kwargs) -> QuerySet:
        queryset = super().get_queryset()
        if self.request.user.is_staff or MailingSettings.owner == self.request.user:
            return queryset
        raise Http404

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['mailing_logs'] = MailingLog.objects.all()
        context['mailing'] = MailingSettings.objects.first()
        context['title'] = 'Рассылки'
        return context

    def test_func(self) -> bool:
        return self.request.user.groups.filter(name='service_users')


class MailingDetailPage(DetailView):
    '''Класс для отображения информации об одной рассылке'''
    model = MailingSettings
    template_name = 'mailing_detail.html'

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        group = self.request.user.groups.filter(name='manager')
        status = self.get_object().status

        if not group:
            if not check_user(self.get_object().user, self.request.user):
                return redirect('myapp:mailing_list')
        else:
            if status == get_status_object('завершена'):
                return redirect('myapp:manager_mailing_list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title

        return context


class DeleteMailing(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    '''Класс для удаления рассылки'''
    model = MailingSettings
    template_name = 'delete_mailing.html'
    success_url = reverse_lazy('myapp:mailing_list')
    permission_required = 'myapp.delete_mail'

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        mailing = self.get_object()
        group = self.request.user.groups.filter(name='manager')

        if not group:
            if not check_user(mailing.user, self.request.user) or check_mailing_status(mailing, 'запущена'):
                return redirect('myapp:mailing_list')
        elif self.get_object().status != get_status_object('создана'):
            return redirect('myapp:manager_mailing_list')

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        group = self.request.user.groups.filter(name='manager')

        if group:
            return reverse('myapp:manager_mailing_list')

        return reverse('myapp:mailing_list')

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление рассылки {self.object.title}'

        return context


class MailLogfileDetailView(DetailView):
    model = MailingSettings
    template_name = 'mailing/logfile_list.html'


def toggle_activity(request, pk):
    mail = MailingSettings.objects.get(pk=pk)
    if mail.is_going:
        mail.is_going = False
    else:
        mail.is_going = True

    mail.save()
    return redirect(reverse('myapp:mailing_list'))


def mailing_activity(request, pk):
    mailing = get_object_or_404(MailingSettings, pk=pk)
    if mailing.status:
        mailing.status = False
    else:
        mailing.status = True
    mailing.save()
    return redirect(reverse('myapp:mail_list'))


class ChangeMailingStatusView(LoginRequiredMixin, PermissionRequiredMixin, View):
    '''Класс для перевода рассылки к типу "завершена"'''

    permission_required = 'myapp.change_mailingstatus'

    def __get_mailing(self, slug) -> MailingSettings:
        mailing = get_object_or_404(MailingSettings, slug=slug)

        return mailing

    def get(self, request, slug) -> HttpResponse:
        mailing = self.__get_mailing(slug)
        group = self.request.user.groups.filter(name='manager')

        if not group:
            if not check_user(mailing.user, self.request.user) or not check_mailing_status(mailing, 'запущена'):
                return redirect('myapp:mailing_list')
        elif not check_mailing_status(mailing, 'запущена'):
            return redirect('myapp:manager_mailing_list')

        return render(
            request, 'myapp/mailing_status_change.html',
            {'object': mailing, 'title': 'Изменение статуса'}
        )

    def post(self, request, slug) -> HttpResponse:
        mailing = self.__get_mailing(slug)
        mailing.status = MailingStatus.objects.get(name='завершена')
        mailing.save()

        group = self.request.user.groups.filter(name='manager')

        if group:
            return redirect('myapp:manager_mailing_list')

        return redirect('myapp:mailing_list')


###########################################################################


"""Блок логов"""

class MailingLogsListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    '''
    Класс для просмотра всех логов рассылок
    '''
    model = MailingLog
    permission_required = 'mailings.view_mailinglogs'
    template_name = 'myapp/mailing_logs_list.html'

    def get_queryset(self, *args, **kwargs) -> MailingLog:
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(mailing__user=self.request.user).order_by('-attempt_datetime')

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Логи рассылок'

        return context


class ManagerMailingListView(MailingList):
    '''Класс для отображения страницы всех активных рассылок для менеджера'''
    template_name = 'myapp/manager_mailing_list.html'
    permission_required = 'myapp.view_mailing'

    def get_queryset(self, *args, **kwargs) -> QuerySet:
        queryset = MailingSettings.objects.filter(
            Q(status=get_status_object('запущена')) |
            Q(status=get_status_object('создана'))
        )

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Активные рассылки'

        return context

    def test_func(self) -> bool:
        return self.request.user.is_staff




# '''это старый код'''
#
# class CreateMailingLog(CreateView):
#     model = MailingLog
#     form_class = MailingLogForm
#     template_name = 'create_mailing_log.html'
#     success_url = reverse_lazy('myapp:log_list')
#
#     def form_valid(self, form):
#         send_time = form.cleaned_data['send_time']
#         mailing = MailingSettings.objects.get(pk=self.kwargs['mailing_id'])
#         client = form.cleaned_data['client']
#         mailing_log = form.save(commit=False)
#         mailing_log.mailing = mailing
#         mailing_log.send_datetime = timezone.now()
#         mailing_log.status = 'attempted'
#         mailing_log.save()
#         return super().form_valid(form)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['mailing'] = MailingSettings.objects.get(pk=self.kwargs['mailing_id'])
#         return context
#
#
# class LogList(LoginRequiredMixin, ListView):
#     model = MailingLog
#     template_name = 'log_list.html'
#     context_object_name = 'log_list'
#
#
# class LogDetail(LoginRequiredMixin, DetailView):
#     model = MailingLog
#     template_name = 'log_detail.html'
#     context_object_name = 'log'

