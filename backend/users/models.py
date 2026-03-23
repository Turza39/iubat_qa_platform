from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Email is required')
        if not username:
            raise ValueError('Username is required')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):

    VERIFICATION_STATUS_CHOICES = [
        ('not_submitted', 'Not Submitted'),
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    username              = models.CharField(max_length=50, unique=True)
    email                 = models.EmailField(unique=True)
    verification_status   = models.CharField(
                                max_length=20,
                                choices=VERIFICATION_STATUS_CHOICES,
                                default='not_submitted'
                            )
    is_active             = models.BooleanField(default=True)
    is_staff              = models.BooleanField(default=False)
    date_joined           = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

    @property
    def is_verified(self):
        return self.verification_status == 'verified'


class VerificationRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    user          = models.OneToOneField(
                        User,
                        on_delete=models.CASCADE,
                        related_name='verification_request'
                    )
    id_card_image = models.ImageField(upload_to='verification_images/')
    status        = models.CharField(
                        max_length=20,
                        choices=STATUS_CHOICES,
                        default='pending'
                    )
    submitted_at  = models.DateTimeField(auto_now_add=True)
    reviewed_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'verification_requests'

    def __str__(self):
        return f'{self.user.username} - {self.status}'