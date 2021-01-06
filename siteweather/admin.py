from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from siteweather.models import CityBlock, CustomUser
from .admin_panel.forms import CustomUserAdminForm, GroupAdminForm
from .utils import make_premium, make_standard

admin.site.unregister(Group)


class CityBlockInline(admin.TabularInline):
    model = CityBlock
    extra = 1
    max_num = 5
    fields = ('timestamp', 'city_name', 'weather_full_description', 'temperature')
    readonly_fields = fields
    ordering = ('-timestamp',)


@admin.register(CityBlock)
class CityBlockAdmin(ModelAdmin):
    list_display = (
        'city_name', 'weather_main_description', 'weather_full_description', 'timestamp', 'temperature', 'wind_speed',
        'humidity', 'pressure', 'searched_by_user')
    list_display_links = ('city_name',)
    list_filter = ('city_name', 'timestamp')
    list_per_page = 20
    search_fields = ('city_name', 'searched_by_user__username')


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm
    list_display = ('username', 'colored_premium', 'email', 'first_name', 'last_name', 'phone_number', 'is_superuser',
                    'date_joined')
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('date_joined', 'is_superuser', 'role',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'email', 'phone_number', 'user_city')}),
        ('Dates related to the account', {'fields': ('last_login', 'date_joined')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role'),
            'description': 'test_desc'})
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )
    list_per_page = 12
    radio_fields = {'role': admin.VERTICAL, }
    save_on_top = True
    actions = [make_premium, make_standard]
    date_hierarchy = 'date_joined'
    readonly_fields = ('groups',)
    inlines = [CityBlockInline]

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return self.fieldsets

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.has_perm('siteweather.delete_customuser'):
            return True
        return False


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    filter_horizontal = ['permissions']
