"""
siteadmin/views.py — All views require is_staff=True.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.auth import get_user_model

from links.models import Link
from .models import (Subscription, SubscriptionPlan, SiteSettings,
                     PlanFeature, PlanFeatureValue)
from .forms import (SiteSettingsForm, AdminUserForm, AdminSetPasswordForm,
                    SubscriptionForm, SubscriptionPlanForm, AdminLinkForm,
                    PlanFeatureForm)

User = get_user_model()
staff_required = user_passes_test(lambda u: u.is_active and u.is_staff, login_url='/login/')


def _ensure_subscription(user):
    sub, created = Subscription.objects.get_or_create(user=user)
    if created:
        free_plan = SubscriptionPlan.objects.filter(slug='free').first()
        if free_plan:
            sub.plan = free_plan
            sub.plan_slug = free_plan.slug
            sub.save(update_fields=['plan', 'plan_slug'])
    return sub


# ── Dashboard ────────────────────────────────────────────────────────────────

@login_required
@staff_required
def admin_dashboard(request):
    total_users  = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    total_links  = Link.objects.count()
    active_links = Link.objects.filter(is_active=True).count()

    plans = SubscriptionPlan.objects.all()
    plan_counts = {p.slug: Subscription.objects.filter(plan=p).count() for p in plans}
    unassigned = User.objects.filter(subscription__isnull=True).count()
    plan_counts['free'] = plan_counts.get('free', 0) + unassigned
    plan_breakdown = [(p.slug, p.name, plan_counts.get(p.slug, 0)) for p in plans]

    recent_users = User.objects.select_related('subscription__plan').order_by('-date_joined')[:8]
    site = SiteSettings.load()

    return render(request, 'siteadmin/dashboard.html', {
        'total_users': total_users, 'active_users': active_users,
        'total_links': total_links, 'active_links': active_links,
        'plan_breakdown': plan_breakdown, 'recent_users': recent_users,
        'site': site, 'plans': plans, 'now': timezone.now(),
    })


# ── Users ─────────────────────────────────────────────────────────────────────

@login_required
@staff_required
def user_list(request):
    q    = request.GET.get('q', '').strip()
    plan = request.GET.get('plan', '')
    users = (User.objects.select_related('subscription__plan')
             .order_by('username').annotate(link_count=Count('links')))
    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q) | Q(name__icontains=q))
    if plan:
        users = users.filter(subscription__plan__slug=plan)
    return render(request, 'siteadmin/user_list.html', {
        'users': users, 'q': q, 'plan': plan,
        'plans': SubscriptionPlan.objects.all(),
    })


@login_required
@staff_required
def user_edit(request, user_id):
    target    = get_object_or_404(User, pk=user_id)
    sub       = _ensure_subscription(target)
    links     = target.links.all().order_by('order')
    user_form = AdminUserForm(instance=target)
    sub_form  = SubscriptionForm(instance=sub)
    pw_form   = AdminSetPasswordForm(user=target)

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'save_user':
            user_form = AdminUserForm(request.POST, instance=target)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, f'User @{target.username} updated.')
                return redirect('admin_user_edit', user_id=user_id)
            messages.error(request, 'Please fix the errors below.')
        elif action == 'save_subscription':
            sub_form = SubscriptionForm(request.POST, instance=sub)
            if sub_form.is_valid():
                sub_form.save()
                messages.success(request, 'Subscription updated.')
                return redirect('admin_user_edit', user_id=user_id)
        elif action == 'set_password':
            pw_form = AdminSetPasswordForm(user=target, data=request.POST)
            if pw_form.is_valid():
                pw_form.save()
                messages.success(request, 'Password changed.')
                return redirect('admin_user_edit', user_id=user_id)
        elif action == 'toggle_active':
            target.is_active = not target.is_active
            target.save(update_fields=['is_active'])
            messages.success(request, f'Account {"enabled" if target.is_active else "disabled"}.')
            return redirect('admin_user_edit', user_id=user_id)
        elif action == 'delete_user':
            uname = target.username
            target.delete()
            messages.success(request, f'User @{uname} deleted.')
            return redirect('admin_user_list')

    return render(request, 'siteadmin/user_edit.html', {
        'target': target, 'sub': sub, 'links': links,
        'user_form': user_form, 'sub_form': sub_form, 'pw_form': pw_form,
    })


# ── Links ─────────────────────────────────────────────────────────────────────

@login_required
@staff_required
def link_edit(request, link_id):
    link = get_object_or_404(Link, pk=link_id)
    form = AdminLinkForm(instance=link)
    if request.method == 'POST':
        if request.POST.get('action') == 'delete':
            uid = link.user_id
            link.delete()
            messages.success(request, 'Link deleted.')
            return redirect('admin_user_edit', user_id=uid)
        form = AdminLinkForm(request.POST, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, 'Link saved.')
            return redirect('admin_user_edit', user_id=link.user_id)
    return render(request, 'siteadmin/link_edit.html', {'link': link, 'form': form})


# ── Subscription Plans ────────────────────────────────────────────────────────

@login_required
@staff_required
def plan_list(request):
    plans = SubscriptionPlan.objects.annotate(sub_count=Count('subscriptions'))
    return render(request, 'siteadmin/plan_list.html', {'plans': plans})


@login_required
@staff_required
def plan_create(request):
    form = SubscriptionPlanForm()
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Plan "{plan.name}" created.')
            return redirect('admin_plan_edit', plan_id=plan.pk)
    return render(request, 'siteadmin/plan_form.html', {'form': form, 'action': 'Create'})


@login_required
@staff_required
def plan_edit(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
    all_features = PlanFeature.objects.all().order_by('order', 'slug')

    if request.method == 'POST':
        if request.POST.get('action') == 'delete':
            name = plan.name
            plan.delete()
            messages.success(request, f'Plan "{name}" deleted.')
            return redirect('admin_plan_list')

        if request.POST.get('action') == 'save_features':
            # Save all feature values from the feature matrix form
            for feature in all_features:
                val = request.POST.get(f'feat_{feature.slug}', '')
                if feature.feature_type == 'bool':
                    val = 'true' if val == 'true' else 'false'
                PlanFeatureValue.objects.update_or_create(
                    plan=plan, feature=feature,
                    defaults={'value': val},
                )
            messages.success(request, 'Feature settings saved.')
            return redirect('admin_plan_edit', plan_id=plan_id)

        form = SubscriptionPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, f'Plan "{plan.name}" saved.')
            return redirect('admin_plan_edit', plan_id=plan_id)
    else:
        form = SubscriptionPlanForm(instance=plan)

    # Build feature value map for the form
    existing = {pfv.feature_id: pfv.value
                for pfv in plan.feature_values.select_related('feature')}
    feature_rows = []
    for feat in all_features:
        current_val = existing.get(feat.id, feat.default_value)
        feature_rows.append({'feature': feat, 'value': current_val})

    return render(request, 'siteadmin/plan_form.html', {
        'form': form, 'plan': plan, 'action': 'Edit',
        'sub_count': plan.subscriptions.count(),
        'feature_rows': feature_rows,
    })


@login_required
@staff_required
def plan_toggle_home(request, plan_id):
    if request.method != 'POST':
        return redirect('admin_plan_list')
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
    plan.show_on_home = not plan.show_on_home
    plan.save(update_fields=['show_on_home'])
    state = 'visible' if plan.show_on_home else 'hidden'
    messages.success(request, f'Plan "{plan.name}" is now {state} on the home page.')
    return redirect('admin_plan_list')


# ── Feature catalogue management ─────────────────────────────────────────────

@login_required
@staff_required
def feature_list(request):
    features = PlanFeature.objects.all()
    plans = SubscriptionPlan.objects.prefetch_related('feature_values__feature')
    return render(request, 'siteadmin/feature_list.html', {
        'features': features, 'plans': plans,
    })


@login_required
@staff_required
def feature_create(request):
    form = PlanFeatureForm()
    if request.method == 'POST':
        form = PlanFeatureForm(request.POST)
        if form.is_valid():
            feat = form.save()
            messages.success(request, f'Feature "{feat.name}" created.')
            return redirect('admin_feature_list')
    return render(request, 'siteadmin/feature_form.html', {'form': form, 'action': 'Create'})


@login_required
@staff_required
def feature_edit(request, feature_id):
    feat = get_object_or_404(PlanFeature, pk=feature_id)
    form = PlanFeatureForm(instance=feat)
    if request.method == 'POST':
        if request.POST.get('action') == 'delete':
            feat.delete()
            messages.success(request, 'Feature deleted.')
            return redirect('admin_feature_list')
        form = PlanFeatureForm(request.POST, instance=feat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feature saved.')
            return redirect('admin_feature_list')
    return render(request, 'siteadmin/feature_form.html', {
        'form': form, 'feat': feat, 'action': 'Edit',
    })


# ── Site Settings ─────────────────────────────────────────────────────────────

@login_required
@staff_required
def site_settings(request):
    obj  = SiteSettings.load()
    form = SiteSettingsForm(instance=obj)
    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site settings saved.')
            return redirect('admin_site_settings')
    accent_presets = [
        ('#ff4d00','Orange'), ('#2563eb','Blue'),   ('#16a34a','Green'),
        ('#7c3aed','Purple'), ('#dc2626','Red'),     ('#d97706','Amber'),
        ('#0891b2','Cyan'),   ('#db2777','Pink'),    ('#f0f0f0','White'),
        ('#111111','Black'),
    ]
    return render(request, 'siteadmin/site_settings.html', {
        'form': form, 'obj': obj, 'accent_presets': accent_presets,
    })
