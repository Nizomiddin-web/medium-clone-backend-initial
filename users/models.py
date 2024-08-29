from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class CustomUser(AbstractUser):
    """This model represent a custom user"""
    middle_name = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]  # describing order joined

    def __str__(self):
        """This method returns the full name of the user"""
        if self.full_name:
            return self.full_name
        else:
            return self.email or self.username

    @property
    def full_name(self):
        """This function return user's full name."""
        return f"{self.last_name} {self.first_name} {self.middle_name}"
