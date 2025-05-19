from django.db import models  # noqa: D100, EXE002


class News(models.Model):
    """Новости.

    Attributes:
        name (str): Название новости
        text (str): Текст новости
        image (ImageField): Изображение новости
        created_at (DateTimeField): Дата создания

    """

    name = models.CharField(max_length=255)
    text = models.TextField()
    image = models.ImageField(upload_to="news/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:  # noqa: D106
        verbose_name = "Новости"
        verbose_name_plural = "Новости"

    def __str__(self) -> str: return self.name  # noqa: D105

    def short_content(self) -> str:
        """Краткое содержание новости."""
        return self.text[:100] + ("..." if len(self.text) > 100 else "")  # noqa: PLR2004
