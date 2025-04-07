from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings

from shop.models import Cart

def add_tables(user):
    _ = Cart.objects.create(user=user)
    Profile.objects.create(
        user=user,
        address='N/A',
        gender='M',
        car_type='other',
        country='N/A',
        city='N/A',
        zip_code='N/A'
    )


class CustomUserManager(BaseUserManager):
    """Custom manager for CustomUser model with support for superuser creation."""

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.create_user(username, email, password, last_name='Admin', first_name='Super', middle_name='User', birth_date='2000-01-01', **extra_fields)
        add_tables(user)

        return user


class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True, verbose_name="Логин", blank=False)
    last_name = models.CharField(max_length=150, verbose_name="Фамилия", blank=False)
    first_name = models.CharField(max_length=150, verbose_name="Имя", blank=False)
    middle_name = models.CharField(max_length=150, verbose_name="Отчество", blank=False)
    birth_date = models.DateField(verbose_name="Дата рождения", blank=False)
    email = models.EmailField(verbose_name="E-mail адрес", blank=False)

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"

    def __str__(self):
        return self.username



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile", verbose_name="Покупатель")
    address = models.TextField(verbose_name="Адрес", blank=True)
    country = models.CharField(max_length=20, verbose_name="Страна", blank=True)
    city = models.CharField(max_length=20, verbose_name="Город", blank=True)
    zip_code = models.CharField(max_length=10, verbose_name="Почтовый индекс", blank=True)

    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Пол", blank=True, default='M')

    CAR_TYPE_CHOICES = [
        ('passenger', 'Легковой'),
        ('cargo', 'Грузовой'),
        ('other', 'Другое'),
    ]
    car_type = models.CharField(max_length=10, choices=CAR_TYPE_CHOICES, verbose_name="Тип автомобиля", blank=True)

    def __str__(self):
        return f"Профиль {self.user.username}"
