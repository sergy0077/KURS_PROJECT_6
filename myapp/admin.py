from django.contrib import admin
from .models import MailingSettings, Client, Message, MailingLog, User


admin.site.register(MailingSettings)
admin.site.register(Client)
admin.site.register(Message)
admin.site.register(MailingLog)
admin.site.register(User)


