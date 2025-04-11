from django import forms
from phonenumber_field.formfields import PhoneNumberField
from django.contrib.auth import get_user_model
from accounts.models import Profile


class CheckoutForm(forms.Form):
    address = forms.CharField(label="Адрес доставки:", max_length=100)
    phone = PhoneNumberField(label="Номер телефона:", region="RU")


User = get_user_model()

class OrderForm(forms.ModelForm):
    full_name = forms.CharField(
        label="Полное имя",
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "input validator w-full border px-4 py-2",
            "placeholder": "Иван Иванович Петров",
            "required": True,
        })
    )

    email = forms.EmailField(
        label="Электронная почта",
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "input validator w-full border px-4 py-2",
            "type": "email",
            "placeholder": "my_email@yandex.ru",
        })
    )

    recipient = forms.CharField(
        label="Получатель",
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "input validator w-full border px-4 py-2",
            "placeholder": "Имя получателя",
        })
    )

    comment = forms.CharField(
        label="Комментарий к заказу",
        required=False,
        widget=forms.Textarea(attrs={
            "class": "textarea w-full border px-4 py-2",
            "rows": 3,
            "placeholder": "Дополнительные пожелания",
        })
    )

    class Meta:
        model = Profile
        fields = ["address", "country", "city", "zip_code"]
        widgets = {
            "address": forms.TextInput(attrs={
                "class": "input validator w-full border px-4 py-2",
                "placeholder": "Улица, дом, квартира",
                "required": True,
            }),
            "city": forms.TextInput(attrs={
                "class": "input validator w-full border px-4 py-2",
                "placeholder": "Москва",
                "required": True,
            }),
            "zip_code": forms.TextInput(attrs={
                "class": "input validator tabular-nums w-full border px-4 py-2",
                "pattern": r'^\d{6}$',
                "minlength": "6",
                "maxlength": "6",
                "placeholder": "123456",
                "title": "Должно быть шесть цифр без пробелов",
                "required": True,
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["full_name"].initial = f"{user.first_name} {user.middle_name} {user.last_name}".strip()
            self.fields["email"].initial = user.email
            if hasattr(user, "profile"):
                self.fields["address"].initial = user.profile.address if user.profile.address != "N/A" else ""
                self.fields["country"].initial = user.profile.country if user.profile.country != "N/A" else ""
                self.fields["city"].initial = user.profile.city if user.profile.city != "N/A" else "Россия"
                self.fields["zip_code"].initial = user.profile.zip_code if user.profile.zip_code != "N/A" else ""

    def clean_zip_code(self):
        zip_code = self.cleaned_data.get("zip_code")
        if not zip_code.isdigit() or len(zip_code) not in [5, 6, 10]:
            raise forms.ValidationError("Введите корректный почтовый индекс.")
        return zip_code
