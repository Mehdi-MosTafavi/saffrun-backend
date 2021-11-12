from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from authentication.views import RegisterUser, ChangePassword

app_name = "auth"
urlpatterns = [
    path("register/", RegisterUser.as_view(), name="register"),
    path("login/", jwt_views.TokenObtainPairView.as_view(), name="login"),
    path("logout/", jwt_views.TokenRefreshView.as_view(), name="logout"),
    path("verify/", jwt_views.TokenVerifyView.as_view(), name="verify"),
    path("change_password/", ChangePassword.as_view(), name="change_password"),
]
