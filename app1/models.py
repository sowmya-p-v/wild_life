from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# Custom User Model extending AbstractUser
class UserRegistration(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name="userregistration_groups",  # Avoid conflict
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="userregistration_permissions",  # Avoid conflict
        blank=True
    )
    # def is_researcher(self):
    #     return self.groups.filter(name="Researchers").exists()

    def __str__(self):
        return self.username

   


# Image Model for storing uploaded images
class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')

    def __str__(self):
        return f"Image {self.id}"
