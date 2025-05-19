from smtplib import SMTPException  # noqa: D100, EXE002

import structlog
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect

logger = structlog.get_logger(__name__)


def send_email(request) -> HttpResponse | None:  # noqa: ANN001
    """Отправка электронной почты."""
    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        email = request.POST.get("email", "").strip()
        name = request.POST.get("name", "").strip()
        details = f"Cоздано новое обращение! \n \nИмя: {name} \nПочта: {email} \nСообщение: {message}"  # noqa: RUF001

        if not message:
            return HttpResponse("Сообщение не может быть пустым!", status=400)

        email = EmailMessage(
            subject="Создано обращение",
            body=details,
            from_email="easyparking673@gmail.com",
            to=["easyparking673@gmail.com"],
        )
        try:
            email.send(fail_silently=False)
            logger.info("Email sent successfully")
            return redirect("home")
        except SMTPException as e:
            logger.error('Error sending email', exc_info=e)
            return None
    return None
