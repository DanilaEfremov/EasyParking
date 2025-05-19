from django.db import models  # noqa: D100


class AbstractCRUD[M: models.Model, I]:
    """Абстрактные методы для создания, чтения, изменения и удаления записи из модели.

    M - тип (модель) объекта.
    I - тип первичного индекса (pk).
    """

    def create(self, *args, **kwargs) -> M|None:  # noqa: ANN002, ANN003, ARG002
        """Создание записи в модели."""
        return None

    def read(self, pk: I) -> M|None:  # noqa: ARG002
        """Чтение записи с ключом pk."""  # noqa: RUF002
        return None

    def update(self, pk: I, *args, **kwargs) -> bool:  # noqa: ANN002, ANN003, ARG002
        """Изменение записи с ключом pk."""  # noqa: RUF002
        return False

    def delete(self, pk: I) -> bool:  # noqa: ARG002
        """Удаление записи с ключом pk."""  # noqa: RUF002
        return False

