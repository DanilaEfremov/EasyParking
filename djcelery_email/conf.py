from appconf import AppConf  # noqa: D100, EXE002


class DjangoCeleryEmailAppConf(AppConf):  # noqa: D101
    class Meta:  # noqa: D106
        prefix = "CELERY_EMAIL"

    TASK_CONFIG = {}  # noqa: RUF012
    BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    CHUNK_SIZE = 10
    MESSAGE_EXTRA_ATTRIBUTES = None
