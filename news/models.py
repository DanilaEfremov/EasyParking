from django.db import models


class News(models.Model):
    """Новости
        Attributes:
            name (str): Название новости
            text (str): Текст новости
            image (ImageField): Изображение новости
            created_at (DateTimeField): Дата создания
    """
    name = models.CharField(max_length=255)
    text = models.TextField()
    image = models.ImageField(upload_to='news/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def short_content(self):
        return self.text[:100] + ('...' if len(self.text) > 100 else '')
