from django.shortcuts import render, get_object_or_404
from accounts.models import User


def profile(request, username):
    user  = get_object_or_404(User, username=username)
    links = user.links.filter(is_active=True)
    return render(request, 'public/profile.html', {'profile': user, 'links': links})


def home(request):
    """
    Public home page.  Querying SubscriptionPlan is wrapped in a try/except
    so the page renders correctly on a fresh database before `migrate` has been
    run (avoids OperationalError: no such table on first boot).
    """
    try:
        from siteadmin.models import SubscriptionPlan
        plans = SubscriptionPlan.objects.filter(show_on_home=True).order_by('order', 'id')
    except Exception:
        plans = []
    return render(request, 'home.html', {'plans': plans})
