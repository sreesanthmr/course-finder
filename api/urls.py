from django.urls import path
from .views import *

urlpatterns = [
    path("student_reg/", StudentRegView.as_view()),
    path("college_reg/", CollegeRegView.as_view()),
    path("login/", LoginView.as_view()),
    path("verify_otp/", VerifyOtpView.as_view()),
    path("admin_reg/", AdminRegView.as_view()),
]
