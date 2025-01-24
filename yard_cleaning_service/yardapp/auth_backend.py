from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

class EmailAuthBackend(BaseBackend):
    """
    Authenticate using email and password.
    """
    def authenticate(self, request, email=None, password=None):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):  # Verify the password
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
