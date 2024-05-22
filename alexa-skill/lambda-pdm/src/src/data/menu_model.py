import datetime
from enum import Enum
from typing import List, Optional, Set

from pydantic import BaseModel, Field, field_validator


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
