from django.urls import path
from . import views

urlpatterns = [
    path("",                              views.dashboard,   name="dashboard"),
    path("edit/",                         views.edit_profile, name="edit_profile"),
    path("add-link/",                     views.add_link,    name="add_link"),
    path("edit-link/<int:link_id>/",      views.edit_link,   name="edit_link"),
    path("delete-link/<int:link_id>/",    views.delete_link, name="delete_link"),
]