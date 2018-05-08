from django.contrib import admin
from transaction.models import Notification, Transaction


admin.site.register(Notification)
admin.site.register(Transaction)
