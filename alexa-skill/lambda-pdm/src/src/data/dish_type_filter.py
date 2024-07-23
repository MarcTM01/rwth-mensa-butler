"""Defines various filters for dishes."""

from enum import Enum

from src.data.menu_model import DishType, MensaMenu, NutritionFlag


class DishTypeFilter(str, Enum):
    """Enum for the different types of dishes that can be filtered."""

    VEGETARIAN = "VEGETARIAN"
    VEGAN = "VEGAN"
    CLASSICS = "CLASSICS"
    PASTA = "PASTA"
    WOK = "WOK"
    PIZZA = "PIZZA"
    BURGER = "BURGER"
    TABLE_DISH = "TABLE_DISH"

    def matches(self, dish: MensaMenu) -> bool:  # noqa: PLR0911
        """Check if the dish matches the filter."""
        if self == DishTypeFilter.VEGETARIAN:
            return NutritionFlag.VEGETARIAN in dish.nutrition_flags
        if self == DishTypeFilter.VEGAN:
            return NutritionFlag.VEGAN in dish.nutrition_flags
        if self == DishTypeFilter.CLASSICS:
            return dish.dish_type == DishType.CLASSICS
        if self == DishTypeFilter.PASTA:
            return dish.dish_type == DishType.PASTA
        if self == DishTypeFilter.WOK:
            return dish.dish_type == DishType.WOK
        if self == DishTypeFilter.PIZZA:
            return dish.dish_type in {
                DishType.PIZZA_OF_THE_DAY,
                DishType.PIZZA_CLASSICS,
            }
        if self == DishTypeFilter.BURGER:
            return dish.dish_type in {
                DishType.BURGER_CLASSICS,
                DishType.BURGER_OF_THE_WEEK,
            }
        if self == DishTypeFilter.TABLE_DISH:
            return dish.dish_type in {
                DishType.TABLE_DISH,
                DishType.VEGETARIAN_TABLE_DISH,
            }
        return False
