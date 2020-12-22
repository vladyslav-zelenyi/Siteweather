from django.contrib import messages
from django.contrib.auth.models import Permission


def make_premium(modeladmin, request, queryset):
    if request.user.is_superuser:
        queryset.update(role='Premium')
        for user in queryset:
            permission = Permission.objects.get(codename='see_users')
            user.user_permissions.add(permission)
    else:
        messages.add_message(request, messages.ERROR, 'Forbidden')


make_premium.short_description = 'Grant Premium status to selected Users'


def make_standard(modeladmin, request, queryset):
    if request.user.is_superuser:
        queryset.update(role='Standard')
        for user in queryset:
            permission = Permission.objects.get(codename='see_users')
            user.user_permissions.remove(permission)
    else:
        messages.add_message(request, messages.ERROR, 'Forbidden')


make_standard.short_description = 'Grant Standard status to selected Users'
