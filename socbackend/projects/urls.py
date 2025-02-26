from django.urls import path

from . import views

app_name = "projects"
urlpatterns = [
    path("", views.BasicProjectListView.as_view(), name="project_list"),
    path("<int:pk>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("wishlist/", views.ProjectWishlist.as_view(), name="wishlist"),
    path("preference/", views.ProjectPreference.as_view(), name="prefenrence"),
    path('mentor/profile/', views.MentorProfileView.as_view(), name='mentor-profile'),
    path('mentor/ranklist/<int:project_id>/', views.SaveRankListView.as_view(), name='save-rank-list'),

    # path("add/", views.ProjectAddView.as_view(), name="project_add"),
]
