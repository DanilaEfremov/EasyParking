from basket.models import BasketItem  # noqa: D100
from services.crud import AbstractCRUD


class ItemCRUD(AbstractCRUD[BasketItem, int]):
    """Awferf."""

    def create(self, product_id: int, quality: int) -> BasketItem | None:
        """Создать запись в корзине покупателя."""
        return None
