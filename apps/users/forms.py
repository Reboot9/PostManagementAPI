from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from apps.users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
        Form for creating a new user. Includes all the required fields
        and repeated password validation.
        """

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')


class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating an existing user. Includes all the fields on
    the user, but replaces the password field with admins password
    hash display field.
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')
