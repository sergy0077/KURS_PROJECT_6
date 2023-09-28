from datetime import timezone
from celery.app import task
from django.contrib.auth.views import PasswordResetDoneView, RedirectURLMixin
from django.core.mail import send_mail
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy, reverse

from tasks import send_mailing
from .models import MailingSettings, MailingLog, Client, Message, User, Logfile
from myapp.forms import MailingSettingsForm, ClientForm, MessageForm, MailingLogForm, UserForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from myapp.services import send_block_notification, send_reset_password_mail, check_link
from .utils import send_mailing_task, create_failed_log
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView

from django.shortcuts import render
from blog.models import BlogPost
from django.core.exceptions import ObjectDoesNotExist




def index(request):
    try:
        mailing_all = MailingSettings.objects.count()
    except ObjectDoesNotExist:
        mailing_all = 0

    try:
        mailing_active = MailingSettings.objects.filter(status='запущена').count()
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
    return render(request, 'myapp/confirmation/password_reset_form.html')


class UserResetDoneView(PasswordResetDoneView):
    template_name = "confirmation/password_reset_done.html"


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

class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
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


class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
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


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
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


    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields.pop('status')  # Убираем поле "Status" из формы
        return form


class EditMailing(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = MailingSettings
    fields = ['title', 'message', 'clients', 'send_time', 'frequency', 'status']
    template_name = 'edit_mailing.html'
    success_url = reverse_lazy('myapp:mailing_list')
    permission_required = 'myapp.change_mail'

    def test_func(self):
        # Проверка, что текущий пользователь может редактировать данную запись
        mailing = self.get_object()
        return self.can_be_edited_by(self.request.user, mailing)

    def can_be_edited_by(self, user, mailing):
        # проверкf доступа к редактированию записи
        # является ли пользователь создателем записи
        return user.is_superuser


class MailingList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = MailingSettings
    template_name = 'mailing_list.html'
    context_object_name = 'object_list'
    permission_required = 'myapp.view_mail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing_logs'] = MailingLog.objects.all()
        context['mailing'] = MailingSettings.objects.first()
        return context


class MailingDetailPage(DetailView):
    model = MailingSettings
    template_name = 'mailing_detail.html'


class DeleteMailing(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = MailingSettings
    template_name = 'delete_mailing.html'
    success_url = reverse_lazy('myapp:mailing_list')
    permission_required = 'myapp.delete_mail'

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user:
            raise Http404("Вы не являетесь создателем данной рассылки, у вас нет прав на её удаление.")
        return self.object

    def get_success_url(self):
        return reverse('myapp:mailing_list')


class MailLogfileDetailView(DetailView):
    model = MailingSettings
    template_name = 'mailing/logfile_list.html'


class LogDetail(DetailView):
    model = Logfile


def toggle_activity(request, pk):
    mail = MailingSettings.objects.get(pk=pk)
    if mail.is_going:
        mail.is_going = False
    else:
        mail.is_going = True

    mail.save()
    return redirect(reverse('myapp:mailing_list'))


@require_POST
@login_required
def send_mailing_now(request, pk):
    mailing_settings = get_object_or_404(MailingSettings, pk=pk)
    client_id = 1
    try:
        client = Client.objects.get(pk=client_id)
    except Client.DoesNotExist:
        return HttpResponse('Client not found', status=400)

    try:
        mailing_log = MailingLog.objects.create(
            mailing=mailing_settings,
            client=client,
            send_datetime=timezone.now(),
            status=MailingLog.STATUS_ATTEMPTED,
            response='No response received yet',
        )
        mailing_log.save()
        send_mailing(mailing_settings.id)
    except Client.DoesNotExist:
        # Обработка, если клиент не найден
        create_failed_log(None, 'Client not found')
        return HttpResponse('Client not found', status=400)  # Вернуть сообщение об ошибке и статус 400 (Bad Request)

    return redirect('myapp:mailing_detail', pk=pk)



def contacts(request):
    context_data = {
        'manager': User.objects.filter(groups__name='Manager')[0],
        'content_manager': User.objects.filter(groups__name='Content_manager')[0]
    }
    return render(request, 'mailing/contacts.html', context=context_data)


###########################################################################
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
"""Блок логов"""
class CreateMailingLog(CreateView):
    model = MailingLog
    form_class = MailingLogForm
    template_name = 'create_mailing_log.html'
    success_url = reverse_lazy('myapp:log_list')

    def form_valid(self, form):
        send_time = form.cleaned_data['send_time']
        mailing = MailingSettings.objects.get(pk=self.kwargs['mailing_id'])
        client = form.cleaned_data['client']
        mailing_log = form.save(commit=False)
        mailing_log.mailing = mailing
        mailing_log.send_datetime = timezone.now()
        mailing_log.status = 'attempted'
        mailing_log.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing'] = MailingSettings.objects.get(pk=self.kwargs['mailing_id'])
        return context


class LogList(LoginRequiredMixin, ListView):
    model = MailingLog
    template_name = 'log_list.html'
    context_object_name = 'log_list'


class LogDetail(LoginRequiredMixin, DetailView):
    model = MailingLog
    template_name = 'log_detail.html'
    context_object_name = 'log'

