from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    tax_id = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)


    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        group_name = f"Empresa: {self.name}"
        Group.objects.get_or_create(name=group_name)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users')
    is_company_admin = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user.username}({self.company.name})"


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        group_name = f"Empresa: {self.company.name}"
        group, created = Group.objects.get_or_create(name=group_name)
        self.user.groups.add(group)