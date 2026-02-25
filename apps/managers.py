from django.contrib.auth.models import UserManager
from django.db.models import QuerySet


class CustomUserManager(UserManager):
    use_in_migrations = True

    def _create_user_object(self, phone, email, **extra_fields):
        if not phone:
            raise ValueError("The given phone must be set")
        email = self.normalize_email(email)
        user = self.model(phone=phone, email=email, **extra_fields)
        return user

    def _create_user(self, phone, email, **extra_fields):
        """
        Create and save a user with the given phone, email
        """
        user = self._create_user_object(phone, email, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, phone, email=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("type", 'admin')
        return self._create_user(phone, email, **extra_fields)

    def create_superuser(self, phone, email=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone, email, **extra_fields)


class UserQuerySet(QuerySet):
    def admins(self):
        return self.filter(type="admin")

    def sellers(self):
        return self.filter(type="seller")

    def customers(self):
        return self.filter(type="user")

class AdminUserManager(UserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db).admins()

class SellerUserManager(UserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db).sellers()

class CustomerUserManager(UserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db).customers()
