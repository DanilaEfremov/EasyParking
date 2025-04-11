from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser, Profile
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Электронная почта")
    last_name = forms.CharField(required=True, label="Фамилия")
    first_name = forms.CharField(required=True, label="Имя")
    middle_name = forms.CharField(required=True, label="Отчество")
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Дата рождения"
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2", "last_name", "first_name", "middle_name", "birth_date")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Этот адрес электронной почты уже используется.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("Этот логин уже используется.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["username"]
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    car_type = forms.ChoiceField(
        choices=Profile.CAR_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'select w-full border px-4 lg:w-1/2'
        }),
        required=False
    )

    gender = forms.ChoiceField(
        choices=Profile.GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'select w-full border px-4 py-2 lg:w-1/2'
        }),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'middle_name']  # gender и car_type не добавляем сюда, так как они в Profile
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'input w-full border px-4 py-2 lg:w-1/2',
                'placeholder': 'Введите ваше имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input w-full border px-4 py-2 lg:w-1/2',
                'placeholder': 'Введите вашу фамилию'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'input w-full border px-4 py-2 lg:w-1/2',
                'placeholder': 'Введите вашу отчество'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'profile'):
            self.fields['car_type'].initial = user.profile.car_type
            self.fields['gender'].initial = user.profile.gender

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if hasattr(user, 'profile'):
                profile = user.profile
                profile.car_type = self.cleaned_data.get('car_type')
                profile.gender = self.cleaned_data.get('gender')
                profile.save()
        return user




class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Ваш пароль",
        widget=forms.PasswordInput(attrs={
            "class": "w-full border px-4 py-2 lg:w-1/2",
            "placeholder": "",
        }),
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={
            "class": "w-full border px-4 py-2 lg:w-1/2",
            "placeholder": "",
        }),
    )
    new_password2 = forms.CharField(
        label="Повторите новый пароль",
        widget=forms.PasswordInput(attrs={
            "class": "w-full border px-4 py-2 lg:w-1/2",
            "placeholder": "",
        }),
    )


class AddressUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['country', 'city', 'zip_code', 'address']
        widgets = {
            'country': forms.TextInput(attrs={
                'class': 'input input-warning rounded-none w-full px-4 py-2 lg:w-1/2',
                'placeholder': 'Россия'
            }),
            'city': forms.TextInput(attrs={
                'class': 'input input-warning rounded-none w-full px-4 py-2 lg:w-1/2',
                'placeholder': 'Москва'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'input input-warning validator rounded-none w-full px-4 py-2 lg:w-1/2',
                "pattern": r'^\d{6}$',
                "minlength": "6",
                "maxlength": "6",
                "title": "Должно быть шесть цифр без пробелов",
                'placeholder': '115191'
            }),
            'address': forms.Textarea(attrs={
                'class': 'textarea textarea-warning rounded-none w-full px-4 py-2 lg:w-1/2',
                'cols': '30',
                'rows': '5'
            }),
        }


    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code')
        if not zip_code.isdigit() or len(zip_code) != 6:
            raise forms.ValidationError("Введите корректный 6-значный ZIP-код.")
        return zip_code