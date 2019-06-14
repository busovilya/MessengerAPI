from django.contrib import admin
from django.contrib.auth.models import User


class MyUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'is_active', 'last_login', 'last_message_time']


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
