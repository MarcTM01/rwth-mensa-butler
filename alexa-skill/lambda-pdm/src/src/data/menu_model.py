import datetime
from enum import Enum
from typing import List, Optional, Set

from pydantic import BaseModel, Field, field_validator

from src.utils import localization
from src.utils.localization import I18nFunction


class NutritionFlag(str, Enum):
    """An enumeration of the possible nutrition flags."""

    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    PORK = "pork"
    BEEF = "beef"
    FISH = "fish"
    CHICKEN = "chicken"


class MensaMenuExtra(BaseModel):
    """A model for the extra menu items."""

    name: str = Field(alias="Name")
    description: str = Field(alias="Description")


class MensaMenu(BaseModel):
    """A model for the menu items."""

    name: str = Field(alias="Name")
    contents: List[str] = Field(alias="Contents")
    price: Optional[str] = Field(alias="Price", default=None)
    nutrition_flags: Set[NutritionFlag] = Field(
        alias="NutritionFlags", default_factory=set
    )

    @property
    def dish_type(self) -> "DishType":
        """Get the dish type of the menu item."""
        return DishType.from_name(self.name)

    def generate_content_announcement(self, i18n: I18nFunction) -> str:
        """Generate the announcement string for the menu item.

        :param i18n: The translation function
        :return: The announcement string
        """
        if len(self.contents) == 0:
            return i18n("DISH_CONTENT_EMPTY")
        elif len(self.contents) == 1:
            return self.contents[0]
        else:
            return (
                self.contents[0]
                + i18n("DISH_CONTENT_PRIMARY_SECONDARY_BARRIER")
                + i18n("DISH_CONTENT_FURTHER_CONJUNCTION").join(self.contents[1:])
            )

    def generate_full_announcement(self, i18n: I18nFunction) -> str:
        """Generate the full announcement string for the menu item.

        :param i18n: The translation function
        :return: The announcement string
        """
        content_announcement = self.generate_content_announcement(i18n)
        return i18n(f"ANNOUNCEMENT_PREPOSITION_{self.dish_type.identifier}").format(
            contents=content_announcement, name=self.name
        )

    @field_validator("nutrition_flags", mode="before")
    def parse_nutrition_flags(cls, value):
        """Parse the nutrition flags from the expected input format to a set of NutritionFlag enums.

        Sample input value: {
             "NutritionFlags": {
                "vegetarian": {}
             },
        }
        """
        if isinstance(value, dict):
            return {NutritionFlag(flag) for flag in value.keys()}
        return value


class MensaDayMenus(BaseModel):
    """A model for the dynamodb mensa menu item."""

    date: datetime.date = Field(alias="Date")
    menus: List[MensaMenu] = Field(alias="Menus")
    extras: List[MensaMenuExtra] = Field(alias="Extras")
    mensa_id: str = Field(alias="MensaId")
    LanguageKey: str = Field(alias="LanguageKey")

    def get_menus_by_type(self, dish_type: "DishType") -> List[MensaMenu]:
        """Get the menus by the dish type."""
        return [menu for menu in self.menus if menu.dish_type == dish_type]

    def generate_extras_announcement(self, i18n: I18nFunction) -> str:
        """Generate the announcement string for the extra menu items.

        :param i18n: The translation function
        :return: The announcement string
        """
        if len(self.extras) == 0:
            return i18n("EXTRAS_EMPTY")
        return i18n("EXTRAS_FORMAT").format(
            localization.build_localized_list(
                i18n, [extra.description for extra in self.extras]
            )
        )


class DishType(Enum):
    """An enumeration of the possible dish types."""

    TABLE_DISH = ("TABLE_DISH", "Tellergericht", "Stew")
    VEGETARIAN_TABLE_DISH = (
        "VEGETARIAN_TABLE_DISH",
        "Tellergericht vegetarisch",
        "Vegetarian table dish",
    )
    VEGETARIAN = ("VEGETARIAN", "Vegetarisch", "Vegetarian")
    CLASSICS = ("CLASSICS", "Klassiker", "Classics")
    PASTA = ("PASTA", "Pasta", "Pasta")
    WOK = ("WOK", "Wok", "Wok")
    PIZZA_OF_THE_DAY = ("PIZZA_OF_THE_DAY", "Pizza des Tages", "Pizza of the Day")
    PIZZA_CLASSICS = ("PIZZA_CLASSICS", "Pizza Classics", "Pizza classics")
    BURGER_CLASSICS = ("BURGER_CLASSICS", "Burger Classics", "Burger classics")
    BURGER_OF_THE_WEEK = (
        "BURGER_OF_THE_WEEK",
        "Burger der Woche",
        "Burger of the week",
    )
    UNKNOWN = ("UNKNOWN", "-", "-")

    identifier: str
    name_de: str
    name_en: str

    def __init__(self, identifier: str, name_de: str, name_en: str):
        """Initialize the dish type.

        :param identifier: The identifier of the dish type
        :param name_de: The name of the dish type in German
        :param name_en: The name of the dish type in English
        """
        self.identifier = identifier
        self.name_de = name_de
        self.name_en = name_en

    @classmethod
    def from_name(cls, name: str) -> "DishType":
        """Get the dish type from the name."""
        for dish_type in cls:
            if name in [dish_type.name_de, dish_type.name_en]:
                return dish_type
        return cls.UNKNOWN