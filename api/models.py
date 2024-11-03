from django.db import models
from .manager import UserManager
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone


class Location(models.Model):
    location_name = models.CharField(max_length=200)


class CustomUser(AbstractBaseUser):
    
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False) 
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password"]

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    def __str__(self):
        return self.email


class Student(CustomUser):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    plustwo_percentage = models.IntegerField(null=True)
    otp = models.CharField(max_length=6,null=True)
    otp_expiry =models.DateTimeField(null=True)


class Course(models.Model):
    course_type = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class College(CustomUser):
    college_name = models.CharField(max_length=200)
    college_logo = models.ImageField(null=True)
    location_id = models.ForeignKey(Location,on_delete=models.CASCADE)
    courses_id = models.ManyToManyField(Course)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


# class CollegeRegRequest(models.Model):
#     college = models.ForeignKey(College,on_delete=models.CASCADE)
    