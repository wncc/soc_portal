from django.urls import path
from . import views
from projects.views import DomainProjectListView

app_name = "domains"

urlpatterns = [
    # Domain listing and creation
    path("", views.DomainListView.as_view(), name="domain-list"),

    # All domains including inactive (manager dashboard)
    path("all/", views.AllDomainsForManagerView.as_view(), name="domain-list-all"),

    # Domain detail, edit, delete
    path("<str:slug>/", views.DomainDetailView.as_view(), name="domain-detail"),

    # Domain-scoped project list
    path("<str:slug>/projects/", DomainProjectListView.as_view(), name="domain-projects"),

    # Domain members management
    path("<str:slug>/members/", views.DomainMembersView.as_view(), name="domain-members"),
    path("<str:slug>/members/<int:membership_id>/", views.DomainMemberDetailView.as_view(), name="domain-member-detail"),
]

