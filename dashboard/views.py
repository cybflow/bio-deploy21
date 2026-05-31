"""
dashboard/views.py
------------------
All views enforce subscription-based feature gating.
Helper get_user_plan(user) returns the user's active Subscription or None.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import ProfileForm, ThemeForm, LinkForm, PremiumProfileForm
from links.models import Link
from siteadmin.models import (
    FEATURE_PROFILE_THEMES, FEATURE_CUSTOM_FONTS, FEATURE_CUSTOM_LAYOUT,
    FEATURE_BACKGROUND_IMAGE, FEATURE_CUSTOM_COLORS, FEATURE_MAX_LINKS,
    FEATURE_USERNAME_CHANGES, FEATURE_EXTRA_PROFILES, FEATURE_SEO_TAGS,
    FEATURE_ANALYTICS, FEATURE_REMOVE_BADGE,
)


def _sub(user):
    """Return user's Subscription or None."""
    try:
        return user.subscription
    except Exception:
        return None


def _link_limit(user):
    """Return (max_links, current_count). max=0 means unlimited."""
    sub = _sub(user)
    limit = sub.feature_limit(FEATURE_MAX_LINKS) if sub else 5
    current = user.links.count()
    return limit, current


# ── Dashboard home ────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user  = request.user
    sub   = _sub(user)
    links = user.links.all()
    limit, count = _link_limit(user)

    return render(request, 'dashboard/home.html', {
        'links':      links,
        'sub':        sub,
        'link_limit': limit,
        'link_count': count,
        'link_at_limit': limit > 0 and count >= limit,
        'has_analytics':    user.has_feature(FEATURE_ANALYTICS),
        'has_seo':          user.has_feature(FEATURE_SEO_TAGS),
        'has_extra_profiles': user.feature_limit(FEATURE_EXTRA_PROFILES) > 0,
        'has_remove_badge': user.has_feature(FEATURE_REMOVE_BADGE),
    })


# ── Profile editing ───────────────────────────────────────────────────────────

@login_required
def edit_profile(request):
    user = request.user
    sub  = _sub(user)
    old_username = user.username

    form = ProfileForm(instance=user, user=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user, user=user)
        if form.is_valid():
            new_username = form.cleaned_data.get('username')
            changing_username = new_username and new_username != old_username

            if changing_username:
                allowed, reason = user.can_change_username()
                if not allowed:
                    messages.error(request, reason)
                    return render(request, 'dashboard/edit_profile.html',
                                  {'form': form, 'sub': sub})
                form.save()
                user.record_username_change()
            else:
                form.save()

            messages.success(request, 'Profile updated.')
            return redirect('dashboard')

    changes_used  = user.username_changes_this_month()
    sub_obj       = _sub(user)
    changes_limit = sub_obj.feature_limit(FEATURE_USERNAME_CHANGES) if sub_obj else 1

    return render(request, 'dashboard/edit_profile.html', {
        'form': form, 'sub': sub,
        'changes_used':  changes_used,
        'changes_limit': changes_limit,
        'changes_unlimited': changes_limit == 0,
    })


# ── Theme editing ─────────────────────────────────────────────────────────────

@login_required
def edit_theme(request):
    user = request.user
    sub  = _sub(user)

    # Feature flags
    can_themes   = user.has_feature(FEATURE_PROFILE_THEMES)
    can_fonts    = user.has_feature(FEATURE_CUSTOM_FONTS)
    can_layout   = user.has_feature(FEATURE_CUSTOM_LAYOUT)
    can_bg       = user.has_feature(FEATURE_BACKGROUND_IMAGE)
    can_colors   = user.has_feature(FEATURE_CUSTOM_COLORS)

    form = ThemeForm(instance=user, can_themes=can_themes,
                     can_colors=can_colors, can_bg=can_bg)

    if request.method == 'POST':
        form = ThemeForm(request.POST, request.FILES, instance=user,
                         can_themes=can_themes, can_colors=can_colors, can_bg=can_bg)
        if form.is_valid():
            updated_user = form.save(commit=False)

            # Enforce: non-premium users locked to 'default' theme
            if not can_themes:
                updated_user.theme = 'default'

            # Enforce: non-premium users cannot change colors
            if not can_colors:
                updated_user.color_primary = user.color_primary
                updated_user.color_bg      = user.color_bg
                updated_user.color_text    = user.color_text

            # Background image gating
            if not can_bg:
                if updated_user.bg_image and updated_user.bg_image != user.bg_image:
                    messages.error(request, 'Background images require a Pro plan or higher.')
                    return render(request, 'dashboard/edit_theme.html', {
                        'form': form, 'sub': sub,
                        'can_themes': can_themes, 'can_fonts': can_fonts,
                        'can_layout': can_layout, 'can_bg': can_bg, 'can_colors': can_colors,
                    })
            else:
                if request.POST.get('clear_bg_image') == '1':
                    if user.bg_image:
                        user.bg_image.delete(save=False)
                    updated_user.bg_image = ''

            updated_user.save()
            messages.success(request, 'Theme saved.')
            return redirect('dashboard')

    return render(request, 'dashboard/edit_theme.html', {
        'form': form, 'sub': sub,
        'can_themes': can_themes, 'can_fonts': can_fonts,
        'can_layout': can_layout, 'can_bg': can_bg, 'can_colors': can_colors,
    })


# ── Premium profile customisation (fonts + layout) ───────────────────────────

@login_required
def edit_premium_profile(request):
    user = request.user
    sub  = _sub(user)

    can_fonts  = user.has_feature(FEATURE_CUSTOM_FONTS)
    can_layout = user.has_feature(FEATURE_CUSTOM_LAYOUT)

    if not can_fonts and not can_layout:
        messages.error(request,
            'Font and layout customisation require a Pro plan or higher.')
        return redirect('dashboard')

    form = PremiumProfileForm(instance=user,
                               can_fonts=can_fonts, can_layout=can_layout)
    if request.method == 'POST':
        form = PremiumProfileForm(request.POST, instance=user,
                                   can_fonts=can_fonts, can_layout=can_layout)
        if form.is_valid():
            u = form.save(commit=False)
            if not can_fonts:
                u.profile_font = user.profile_font
            if not can_layout:
                u.profile_layout = user.profile_layout
            u.save()
            messages.success(request, 'Profile style saved.')
            return redirect('dashboard')

    return render(request, 'dashboard/edit_premium.html', {
        'form': form, 'sub': sub,
        'can_fonts': can_fonts, 'can_layout': can_layout,
    })


# ── Links ─────────────────────────────────────────────────────────────────────

@login_required
def add_link(request):
    user = request.user
    limit, count = _link_limit(user)

    if limit > 0 and count >= limit:
        messages.error(request,
            f'You have reached your plan limit of {limit} link{"s" if limit != 1 else ""}. '
            'Upgrade your plan to add more links.')
        return redirect('dashboard')

    form = LinkForm()
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            link      = form.save(commit=False)
            link.user = user
            link.save()
            messages.success(request, 'Link added.')
            return redirect('dashboard')
    return render(request, 'dashboard/add_link.html', {'form': form})


@login_required
def edit_link(request, link_id):
    link = get_object_or_404(Link, id=link_id, user=request.user)
    form = LinkForm(instance=link)
    if request.method == 'POST':
        form = LinkForm(request.POST, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, 'Link updated.')
            return redirect('dashboard')
    return render(request, 'dashboard/edit_link.html', {'form': form, 'link': link})


@login_required
def delete_link(request, link_id):
    link = get_object_or_404(Link, id=link_id, user=request.user)
    if request.method == 'POST':
        link.delete()
        messages.success(request, 'Link deleted.')
        return redirect('dashboard')
    return render(request, 'dashboard/delete_link.html', {'link': link})
