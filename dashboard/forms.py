from django import forms
from accounts.models import User, FONT_CHOICES, LAYOUT_CHOICES
from links.models import Link


class ProfileForm(forms.ModelForm):
    """Profile form — username field is present but enforced via view logic."""

    class Meta:
        model  = User
        fields = ['username', 'name', 'bio', 'avatar', 'github', 'website', 'twitter']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user


class ThemeForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['theme', 'color_primary', 'color_bg', 'color_text', 'bg_image']
        widgets = {
            'theme':         forms.RadioSelect(),
            'color_primary': forms.TextInput(attrs={'type': 'color'}),
            'color_bg':      forms.TextInput(attrs={'type': 'color'}),
            'color_text':    forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, can_themes=False, can_colors=False, can_bg=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not can_themes:
            self.fields['theme'].disabled = True
        if not can_colors:
            self.fields['color_primary'].disabled = True
            self.fields['color_bg'].disabled      = True
            self.fields['color_text'].disabled     = True
        if not can_bg:
            self.fields['bg_image'].disabled = True


class PremiumProfileForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['profile_font', 'profile_layout']
        widgets = {
            'profile_font':   forms.RadioSelect(),
            'profile_layout': forms.RadioSelect(),
        }

    def __init__(self, *args, can_fonts=True, can_layout=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not can_fonts:
            self.fields['profile_font'].disabled = True
        if not can_layout:
            self.fields['profile_layout'].disabled = True


class LinkForm(forms.ModelForm):
    class Meta:
        model  = Link
        fields = ['title', 'url', 'icon']
