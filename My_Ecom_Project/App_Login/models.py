from django.db import models

# Create your models here.
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.utils.translation import gettext_lazy

# to automaticcaly create one to one obejects

from django.db.models.signals import post_save
from django.dispatch import receiver

class MyUserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError('The Email must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=False)
    is_staff = models.BooleanField(
        gettext_lazy('staff status'),
        default=False,
        help_text = gettext_lazy('Designates whether the user can log into this admin site.')
    )

    is_active = models.BooleanField(
        gettext_lazy('active'),
        default=True,
        help_text = gettext_lazy('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
    )

    USERNAME_FIELD = 'email'
    objects = MyUserManager()
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return self.email
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'profile')
    username = models.CharField(max_length=255, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    address_1 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=255, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True) 
         
        
    def __str__(self):
        return self.username + "'s Profile"
        
    def is_fully_filled(self):
        fields_name = [f.name for f in self._meta.get_field()]

        for field_name in fields_name:
            value = getattr(self, field_name)
            if value is None or value=='':
                return False
            return True
            
 
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

    