from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import MailingSettings, Client, Message, User
from threading import current_thread

_requests = {}


def get_current_request():
    t = current_thread()
    if t not in _requests:
        return None
    return _requests[t]


class StyleFormMixin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

#########################################################################
class MailingSettingsForm(forms.ModelForm):
    clients = forms.ModelMultipleChoiceField(queryset=Client.objects.all(), widget=forms.CheckboxSelectMultiple)
    status = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    send_time = forms.TimeField(input_formats=['%H:%M:%S'], widget=forms.TimeInput(format='%H:%M:%S'))

    class Meta:
        model = MailingSettings
        fields = ['title', 'sending_time', 'regularity', 'status']


class MailUpdateForm(forms.ModelForm):

    class Meta:
        model = MailingSettings
        fields = ('title', 'body')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = get_current_request()
        self.fields['clients'].queryset = Client.objects.filter(owner=request.user)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

######################################################################
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']

#######################################################################
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']

########################################################################

class UserRegisterForm(StyleFormMixin, UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class UserForm(StyleFormMixin, UserChangeForm):

    class Meta:
        model = User
        fields = ('email', 'password', 'username', 'fullname', 'comment')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password'].widget = forms.HiddenInput()




