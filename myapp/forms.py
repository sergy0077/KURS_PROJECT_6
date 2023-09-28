from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import MailingSettings, Client, Message, MailingLog, User
from .utils import get_current_request


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
        fields = ['title', 'clients', 'start_time', 'start_date', 'end_date', 'frequency', 'status']


class MailUpdateForm(forms.ModelForm):

    class Meta:
        model = MailingSettings
        fields = ('title', 'body_mess', 'clients')

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
class MailingLogForm(StyleFormMixin, forms.ModelForm):
    send_time = forms.TimeField()

    class Meta:
        model = MailingLog
        fields = ['send_time', 'client']

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




