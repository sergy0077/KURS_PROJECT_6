from django.contrib import admin
from .models import MailingSettings, Client, Message, MailingLog, User, Logfile


admin.site.register(MailingSettings)
admin.site.register(Client)
admin.site.register(Message)
admin.site.register(MailingLog)
admin.site.register(User)
admin.site.register(Logfile)

