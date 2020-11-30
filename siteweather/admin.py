from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .forms import GroupAdminForm
from siteweather.models import CityBlock, CustomUser


admin.site.unregister(Group)


def make_premium(modeladmin, request, queryset):
    queryset.update(role='Premium')


def make_standard(modeladmin, request, queryset):
    queryset.update(role='Standard')


make_premium.short_description = 'Grant Premium status to selected Users'
make_standard.short_description = 'Grant Standard status to selected Users'


@admin.register(CityBlock)
class CityBlockAdmin(ModelAdmin):
    list_display = (
        'city_name', 'weather_main_description', 'weather_full_description', 'timestamp', 'temperature', 'wind_speed',
        'humidity', 'pressure', 'searched_by_user')
    list_display_links = ('city_name',)
    search_fields = ('city_name', 'timestamp')
    list_filter = ('city_name', 'timestamp')
    list_per_page = 10


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'colored_premium', 'email', 'first_name', 'last_name', 'phone_number', 'is_superuser',
    )
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('date_joined', 'is_superuser', 'role')
    fieldsets = (
        (None, {'fields': ('username', 'password', 'role')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'user_city')}),

        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    superuser_fieldsets = ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    list_per_page = 12
    radio_fields = {'role': admin.VERTICAL}
    actions = [make_premium, make_standard]

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj:
            if request.user.is_superuser:
                fields_to_remove = ['user_permissions', 'groups', 'is_superuser', ]
                for field in fields_to_remove:
                    fields.remove(field)
        return fields

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return (self.fieldsets or tuple()) + self.superuser_fieldsets
        return super().get_fieldsets(request, obj)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    filter_horizontal = ['permissions']
