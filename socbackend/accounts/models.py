from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, role, **extra_fields):
        if not username:
            raise ValueError("The Username field is required")
        if not role:
            raise ValueError("The Role field is required")
        user = self.model(username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields['role'] = 'admin'

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('mentee', 'Mentee'),
        ('mentor', 'Mentor'),
    ]

    username = models.CharField(max_length=150)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['role']

    class Meta:
        # Ensure combination of username and role is unique
        constraints = [
            models.UniqueConstraint(fields=['username', 'role'], name='unique_username_role')
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"
    


from django.conf import settings  # Import settings to get the AUTH_USER_MODEL dynamically
from django.db import models
from .options import DepartmentChoices, YearChoices
from django.core.exceptions import ValidationError

def upload_to_location(instance, filename):
    return "profile_pictures/{filename}".format(filename=filename)

def validate_roll_number(value):
    batch_number = int(value[:2])
    if batch_number >= 22:
        if not value[2:3].isalpha() or not value[3:].isdigit() or len(value) != 7:
            raise ValidationError("Enter a valid roll number.")
    else:
        if not (len(value) == 9 and value[2].isalpha() and value[3:5].isalpha() and value[5:6].isdigit() and value[6:].isdigit()):
            raise ValidationError("Enter a valid roll number.")

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Dynamically get the custom user model
        on_delete=models.CASCADE,
        primary_key=True,
    )
    name = models.CharField(max_length=100, blank=True, default="")
    profile_picture = models.ImageField(
        upload_to=upload_to_location, blank=True, default=""
    )
    phone_number = models.CharField(max_length=15, blank=False, null=False)
    roll_number = models.CharField(
        "roll number",
        max_length=9,
        help_text="Required. 9 characters or fewer.",
        validators=[validate_roll_number],
    )
    year = models.CharField(choices=YearChoices.choices, null=False, blank=False, max_length=100)
    department = models.CharField(
        max_length=50, choices=DepartmentChoices.choices, blank=False, null=False
    )
    verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=32, blank=True, default="")

    ROLE_CHOICES = [
        ('mentee', 'Mentee'),
        ('mentor', 'Mentor'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='mentee')

    def __str__(self):
        return f"{self.roll_number} - {self.user.username}"
    
    @property
    def is_authenticated(self):
        return self.user.is_authenticated
