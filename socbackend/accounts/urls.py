from django.contrib import admin
from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token_sso/", views.CustomSSOTokenView.as_view(), name="token_obtain_pair_sso"),
    path("profile/", views.UserProfileView.as_view(), name="user_profile"),
    path("register/", views.RegisterUserView.as_view(), name="register_user"),
    path("verify-email/<str:token>/", views.verify_email, name="verify_email"),
    path("departments/", views.DepartmentListAPIView.as_view(), name="department-list"),
    path("years/", views.YearListAPIView.as_view(), name="year-list"),
    path("isloggedin/", views.isloggedin, name="loginstatus"),
    path("logout/", views.logout, name="logout"),
    path("get-sso-user/", views.get_sso_user_data, name="get_sso_user_data"),
    path("register_sso/", views.RegisterUserViewSSO.as_view(), name="register_user_sso"),
    # New multi-domain endpoints
    path("my-memberships/", views.MyMembershipsView.as_view(), name="my-memberships"),
    path("become-manager/<str:secret>/", views.BecomeManagerView.as_view(), name="become-manager"),
]

