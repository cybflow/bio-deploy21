from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.admin_dashboard,   name='admin_dashboard'),
    path('users/',                        views.user_list,         name='admin_user_list'),
    path('users/<int:user_id>/',          views.user_edit,         name='admin_user_edit'),
    path('links/<int:link_id>/',          views.link_edit,         name='admin_link_edit'),
    path('plans/',                        views.plan_list,         name='admin_plan_list'),
    path('plans/create/',                 views.plan_create,       name='admin_plan_create'),
    path('plans/<int:plan_id>/',          views.plan_edit,         name='admin_plan_edit'),
    path('plans/<int:plan_id>/toggle/',   views.plan_toggle_home,  name='admin_plan_toggle'),
    path('features/',                     views.feature_list,      name='admin_feature_list'),
    path('features/create/',              views.feature_create,    name='admin_feature_create'),
    path('features/<int:feature_id>/',    views.feature_edit,      name='admin_feature_edit'),
    path('settings/',                     views.site_settings,     name='admin_site_settings'),
]
