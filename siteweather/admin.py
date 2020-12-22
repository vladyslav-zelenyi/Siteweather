from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .forms import GroupAdminForm
from siteweather.models import CityBlock, CustomUser
from .utils import make_premium, make_standard

admin.site.unregister(Group)


@admin.register(CityBlock)
class CityBlockAdmin(ModelAdmin):
    list_display = (
        'city_name', 'weather_main_description', 'weather_full_description', 'timestamp', 'temperature', 'wind_speed',
        'humidity', 'pressure', 'searched_by_user')
    list_display_links = ('city_name',)
    search_fields = ('city_name',)
    list_filter = ('city_name', 'timestamp')
    list_per_page = 20


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = ('username', 'colored_premium', 'email', 'first_name', 'last_name', 'phone_number', 'is_superuser')
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('date_joined', 'is_superuser', 'role',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'date_of_birth', 'email', 'phone_number',
                                      'user_city')}),
        ('Dates related to the account', {'fields': ('last_login', 'date_joined')}),

    )
    superuser_fieldsets = ('Permissions', {
        'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',),
        'description': '<strong>Description without autoescape from admin.py</strong>',
    }),
    list_per_page = 12
    radio_fields = {'role': admin.VERTICAL}
    save_on_top = True
    actions = [make_premium, make_standard]

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return (self.fieldsets or tuple()) + self.superuser_fieldsets
        return super().get_fieldsets(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.has_perm('siteweather.delete_customuser'):
            return True
        return False


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    filter_horizontal = ['permissions']
