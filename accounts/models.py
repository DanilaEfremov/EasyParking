from django.conf import settings  # noqa: D100, EXE002
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# from shop import models as shop_models
from basket import models as cart_models


class CustomUserManager(BaseUserManager):
    """Custom manager for CustomUser model with support for superuser creation."""

    def create_user(self, username, email, password=None, **extra_fields):  # noqa: ANN003, ANN001, ANN201, D102
        if not email:
            msg = "The Email field must be set"
            raise ValueError(msg)
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):  # noqa: ANN003, ANN001, ANN201, D102
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            msg = "Superuser must have is_staff=True."
            raise ValueError(msg)
        if extra_fields.get("is_superuser") is not True:
            msg = "Superuser must have is_superuser=True."
            raise ValueError(msg)
        user = self.create_user(
            username,
            email,
            password,
            last_name="Admin",
            first_name="Super",
            middle_name="User",
            birth_date="2000-01-01",
            **extra_fields,
        )
        add_tables(user)
        return user


class CustomUser(AbstractUser):
    """Модель, описывающая покупателя."""

    username = models.CharField(max_length=150, unique=True, verbose_name="Логин", blank=False)
    last_name = models.CharField(max_length=150, verbose_name="Фамилия", blank=False)
    first_name = models.CharField(max_length=150, verbose_name="Имя", blank=False)
    middle_name = models.CharField(max_length=150, verbose_name="Отчество", blank=False)
    birth_date = models.DateField(verbose_name="Дата рождения", blank=False)
    email = models.EmailField(verbose_name="E-mail адрес", blank=False)

    objects = CustomUserManager()

    class Meta:  # noqa: D106
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"

    def __str__(self) -> str: return f"{self.last_name} {self.first_name} {self.middle_name}"  # noqa: D105


class Profile(models.Model):
    """Профиль покупателя. Связь с покупателем один к одному."""  # noqa: RUF002

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Покупатель",
    )
    address = models.TextField(verbose_name="Адрес", blank=True)
    country = models.CharField(max_length=20, verbose_name="Страна", blank=True)
    city = models.CharField(max_length=20, verbose_name="Город", blank=True)
    zip_code = models.CharField(max_length=6, verbose_name="Почтовый индекс", blank=True)

    GENDER_CHOICES = [  # noqa: RUF012
        ("M", "Мужской"),
        ("F", "Женский"),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Пол", blank=True, default="M")

    CAR_TYPE_CHOICES = [  # noqa: RUF012
        ("passenger", "Легковой"),
        ("cargo", "Грузовой"),
        ("other", "Другое"),
    ]
    car_type = models.CharField(max_length=10, choices=CAR_TYPE_CHOICES, verbose_name="Тип автомобиля", blank=True)

    def __str__(self) -> str: return f"Профиль {self.user.username}"  # noqa: D105


def add_tables(user: CustomUser) -> None:
    """Создать профиль покупателя."""
    # TODO: Перенести модель из shop в cart и затем исправить в этой функции
    _ = cart_models.Basket.objects.create(user=user)
    Profile.objects.create(
        user=user,
        address="N/A",
        gender="M",
        car_type="other",
        country="Россия",
        city="N/A",
        zip_code="N/A",
    )
