from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from nuddle.apps.AAA.models import User
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _



class UserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('phone_number', 'email', 'first_name', 'last_name')  # Add any other fields as needed
        labels = {
            # Assuming you want to customize these labels on the creation form as well
            'is_superuser': _('Administrator'),
            'is_staff': _('Moderator'),
        }


class UserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields
        labels = {
            'is_superuser': _('Administrator'),
            'is_staff': _('Moderator'),
        }


class UserAdmin(BaseUserAdmin):
    readonly_fields = ('profile_picture_preview',)
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = (
        'phone_number', 'email', 'first_name', 'last_name', 'user_type', 'formatted_created_at', 'formatted_last_active', 'is_staff')
    search_fields = ('phone_number', 'email', 'first_name', 'last_name')
    ordering = ('phone_number',)

    fieldsets = (
        (None, {'fields': ('phone_number', 'email', 'password','user_type')}),
        ('Personal info', {'fields': ('profile_picture_preview', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('formatted_last_active', 'formatted_created_at')}),
    )
    readonly_fields = ('profile_picture_preview', 'formatted_created_at', 'formatted_last_active', 'last_login', 'date_joined')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    def profile_pic(self, obj):
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return format_html('<img src="{}" style="width: 45px; height:45px;" />', obj.profile_picture.url)
        return "-"
    profile_pic.short_description = 'Profile Picture'

    def profile_picture_preview(self, instance):
        if instance.profile_picture:
            return format_html('<img src="{}" style="max-width: 92px; max-height:92px;" />',
                               instance.profile_picture.url)
        return "No picture uploaded."

    profile_picture_preview.short_description = 'Profile Picture Preview'


    def formatted_created_at(self, obj):
        return obj.created_at.strftime('%Y/%m/%d %H:%M')

    formatted_created_at.admin_order_field = 'Date_joined'
    formatted_created_at.short_description = 'Date joined'

    def formatted_last_active(self, obj):
        return obj.last_active.strftime('%Y/%m/%d %H:%M')

    formatted_last_active.admin_order_field = 'last_login'
    formatted_last_active.short_description = 'Last Login'


admin.site.register(User, UserAdmin)
