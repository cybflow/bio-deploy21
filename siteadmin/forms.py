from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from links.models import Link
from .models import Subscription, SubscriptionPlan, SiteSettings, PlanFeature

User = get_user_model()


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model  = SiteSettings
        fields = [
            'site_name', 'tagline', 'site_theme', 'accent_color',
            'allow_signup', 'maintenance', 'maintenance_msg', 'footer_text',
        ]
        widgets = {
            'accent_color':    forms.TextInput(attrs={'type': 'color'}),
            'maintenance_msg': forms.Textarea(attrs={'rows': 3}),
        }


class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model  = SubscriptionPlan
        fields = [
            'slug', 'name', 'price', 'price_label', 'description',
            'features', 'is_featured', 'show_on_home', 'order', 'cta_label',
        ]
        widgets = {
            'features': forms.Textarea(attrs={
                'rows': 7,
                'placeholder': 'One feature per line, e.g.\nUnlimited links\nCustom domain\nClick analytics',
            }),
        }


class AdminUserForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['username', 'name', 'email', 'is_active', 'is_staff']


class AdminSetPasswordForm(SetPasswordForm):
    """Wraps Django's SetPasswordForm with matching widget styling."""
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'admin-input', 'autocomplete': 'new-password'})
        self.fields['new_password1'].help_text = ''
        self.fields['new_password2'].help_text = ''


class SubscriptionForm(forms.ModelForm):
    """
    Admin form for managing a user subscription.
    plan_slug is excluded from the visible fields and instead derived
    automatically from the selected plan FK in save(), so it never
    appears as a required text box and cannot trigger a validation error.
    """
    plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.all(),
        required=False,
        empty_label='— No plan selected —',
        label='Plan',
    )

    class Meta:
        model  = Subscription
        # plan_slug deliberately excluded — it is set programmatically in save()
        fields = ['plan', 'is_active', 'expires_at', 'notes']
        widgets = {
            'expires_at': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'},
            ),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def save(self, commit=True):
        sub = super().save(commit=False)
        # Derive plan_slug from the chosen plan FK; fall back to 'free'
        if sub.plan:
            sub.plan_slug = sub.plan.slug
        elif not sub.plan_slug:
            sub.plan_slug = 'free'
        if commit:
            sub.save()
        return sub


class AdminLinkForm(forms.ModelForm):
    class Meta:
        model  = Link
        fields = ['title', 'url', 'icon', 'order', 'is_active']


class PlanFeatureForm(forms.ModelForm):
    class Meta:
        model  = PlanFeature
        fields = ['slug', 'name', 'description', 'feature_type',
                  'choices_list', 'default_value', 'order']
        widgets = {
            'description': forms.TextInput(),
        }
