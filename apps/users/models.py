from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier.
    """

    def create_user(self, username: str, email: str, password: str = None, **extra_fields) -> "CustomUser":
        """
        Create and save a user with the given email and password.
        :param username: username of the user
        :param email: email address of the user
        :param password: password of the user
        :param extra_fields: additional fields of the user
        :return: the created user object
        """
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username: str, email: str, password: str = None, **extra_fields) -> "CustomUser":
        """
        Create and save a superuser with the given email and password.

        :param username: username of the user
        :param email: email address of the user
        :param password: password of the user
        :param extra_fields: additional fields of the user
        :return: the created superuser object
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports using email instead of username.
    """
    username = models.CharField(unique=True, max_length=255)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: "CustomUserManager" = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email', 'password')

    class Meta:
        ordering = ["username"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
        ]
        verbose_name = "Custom User"
        verbose_name_plural = "Custom Users"

    def __str__(self) -> str:
        return self.username

    def has_perm(self, perm, obj=None) -> bool:
        """
        Check if the user has the specified permission.

        :param perm: The permission string.
        :param obj: The object for which the permission is checked (default: None).
        :return: True if the user has the specified permission, False otherwise.
        """
        return self.is_superuser

    def has_module_perms(self, app_label) -> bool:
        """
        Check if the user has any permissions for the specified app/module.

        :param app_label: The label of the app/module.
        :return: True if the user has any permissions for the specified app/module,
        False otherwise.
        """
        return self.is_superuser
