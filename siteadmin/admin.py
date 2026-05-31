from django.contrib import admin
from .models import (
    Subscription, SubscriptionPlan, SiteSettings,
    PlanFeature, PlanFeatureValue,
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display        = ['name', 'slug', 'price', 'show_on_home', 'is_featured', 'order']
    list_editable       = ['show_on_home', 'is_featured', 'order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields       = ['name', 'slug']


@admin.register(PlanFeature)
class PlanFeatureAdmin(admin.ModelAdmin):
    list_display  = ['name', 'slug', 'feature_type', 'default_value', 'order']
    list_editable = ['order']
    search_fields = ['name', 'slug']


@admin.register(PlanFeatureValue)
class PlanFeatureValueAdmin(admin.ModelAdmin):
    list_display = ['plan', 'feature', 'value']
    list_filter  = ['plan', 'feature']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display  = ['user', 'plan', 'plan_slug', 'is_active', 'started_at', 'expires_at']
    list_filter   = ['plan', 'is_active']
    search_fields = ['user__username', 'user__email', 'plan_slug']
    raw_id_fields = ['user']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'site_theme', 'allow_signup', 'maintenance', 'updated_at']
