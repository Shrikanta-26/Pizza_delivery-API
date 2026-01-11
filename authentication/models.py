from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Email must be provided"))
        if not username:
            raise ValueError(_("Username must be provided"))
        if not phone_number:
            raise ValueError(_("Phone number must be provided"))

        
        extra_fields.setdefault("is_active", True)

        user = self.model(
            email=email,  
            username=username,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True"))

        return self.create_user(
            email=email,
            username=username,
            phone_number=phone_number,
            password=password,
            **extra_fields
        )


class User(AbstractUser):
    username = models.CharField(max_length=25)
    email = models.EmailField(max_length=80, unique=True)
    phone_number = PhoneNumberField(unique=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["username", "phone_number"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
