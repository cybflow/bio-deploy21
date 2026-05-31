from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import SignupForm


def signup(request):
    from siteadmin.models import SiteSettings, Subscription, SubscriptionPlan
    site = SiteSettings.load()
    if not site.allow_signup:
        return render(request, 'accounts/signup_closed.html', {'site': site})

    form = SignupForm()
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-assign the Free plan on every new signup
            free_plan = SubscriptionPlan.objects.filter(slug='free').first()
            Subscription.objects.create(
                user=user,
                plan=free_plan,          # FK (may be None if Free plan not created yet)
                plan_slug='free',
            )
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard')
    return render(request, 'accounts/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
