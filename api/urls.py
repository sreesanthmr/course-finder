from django.urls import path
from .views import *

urlpatterns = [
    path("student_reg/", StudentRegView.as_view()),
    path("college_reg/", CollegeRegView.as_view()),
    path("login/", LoginView.as_view()),
    path("verify_otp/", VerifyOtpView.as_view()),
    path("admin_reg/", AdminRegView.as_view()),
    path("location_reg/", LocationRegView.as_view()),
    path("course_reg/", CourseRegView.as_view()),
    path("admin_approval/", AdminCollegeApprovalView.as_view()),
    path("colleges/", CollegeListView.as_view()),
    path("student_update/", StudentProfileUpdateView.as_view()),
    path("college_update/", CollegeProfileUpdateView.as_view()),
    path("college_details/<int:college_id>/", CollegeDetailsView.as_view()),
    path("search/", SearchView.as_view()),
    path("location_list/", LocationListView.as_view()),
    path("location_based_college_list/<int:location_id>/", LocationBasedCollegeListView.as_view()),
    
]
