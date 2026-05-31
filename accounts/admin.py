from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('name', 'bio', 'avatar', 'github', 'website', 'twitter'),
        }),
        ('Theme', {
            'fields': ('theme', 'color_primary', 'color_bg', 'color_text', 'bg_image'),
        }),
        ('Premium Style', {
            'fields': ('profile_font', 'profile_layout'),
        }),
        ('Username Quota', {
            'fields': (
                'username_changed_at',
                'username_changes_month',
                'username_change_month',
                'username_change_year',
            ),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('username_changed_at',)
