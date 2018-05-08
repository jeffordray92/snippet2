from django.contrib import admin
from message.models import Message, Thread


admin.site.register(Thread)
admin.site.register(Message)