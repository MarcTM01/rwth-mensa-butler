import datetime
from enum import Enum
from typing import Union, cast

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.data.mensas import Mensa
from src.data.menu_model import DishType, MensaDayMenus, MensaMenu, NutritionFlag
from src.handler.intent_handler_with_mensa_and_date import IntentHandlerWithMensaAndDate
from src.utils import alexa_slots
from src.utils.localization import I18nFunction


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

    def matches(self, dish: MensaMenu) -> bool:
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


def _get_dish_type_filter_from_request(
    handler_input: HandlerInput,
) -> Union[Response, DishTypeFilter]:
    _ = cast(
        I18nFunction,
        handler_input.attributes_manager.request_attributes["_"],
    )
    dish_types = alexa_slots.get_slot_ids_from_custom_slot(handler_input, "dishType")
    if dish_types is None or len(dish_types) == 0:
        return handler_input.response_builder.speak(
            _("NO_DISH_TYPE_SPECIFIED")
        ).response

    dish_type = next(iter(dish_types))
    return DishTypeFilter(dish_type)


class GetFilteredMensaOfferingsIntentHandler(IntentHandlerWithMensaAndDate):
    """Handler for GetFilteredMensaOfferingsIntentHandler."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """Overwritten."""
        return ask_utils.is_intent_name("GetFilteredMensaOfferingsIntentHandler")(
            handler_input
        )

    def handle_with_mensa_and_date(
        self,
        handler_input: HandlerInput,
        mensa: Mensa,
        date: datetime.date,
        mensa_offerings: MensaDayMenus,
    ) -> Response:
        """Overwritten."""
        _ = cast(
            I18nFunction,
            handler_input.attributes_manager.request_attributes["_"],
        )
        response_or_filter = _get_dish_type_filter_from_request(handler_input)
        if isinstance(response_or_filter, Response):
            return response_or_filter

        filtered_dishes = [
            menu for menu in mensa_offerings.menus if response_or_filter.matches(menu)
        ]
        if len(filtered_dishes) <= 0:
            speak_output = _("FILTERED_DISH_ANNOUNCEMENT_NO_DISHES").format(
                type=_(f"FILTER_{response_or_filter.value}_PLURAL"),
                mensa=_(mensa.mensaId),
                date=date,
            )
            return handler_input.response_builder.speak(speak_output).response
        elif len(filtered_dishes) == 1:
            speak_output = _("FILTERED_DISH_ANNOUNCEMENT_ONE_DISH").format(
                type=_(f"FILTER_{response_or_filter.value}_SINGLE"),
                mensa=_(mensa.mensaId),
                date=date,
                dish=filtered_dishes[0].generate_full_announcement(_),
            )
            return handler_input.response_builder.speak(speak_output).response
        else:
            speak_output = _("FILTERED_DISH_ANNOUNCEMENT_MULTIPLE_DISHES").format(
                type=_(f"FILTER_{response_or_filter.value}_PLURAL"),
                mensa=_(mensa.mensaId),
                date=date,
                num=len(filtered_dishes),
                dishes=". ".join(
                    map(
                        lambda dish: dish.generate_full_announcement(_), filtered_dishes
                    )
                ),
            )
            return handler_input.response_builder.speak(speak_output).response
