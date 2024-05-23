import datetime
from typing import cast

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.data.mensas import Mensa
from src.data.menu_model import MensaDayMenus, NutritionFlag
from src.handler.intent_handler_with_mensa_and_date import IntentHandlerWithMensaAndDate
from src.utils.localization import I18nFunction


class GetVeganOrVegetarianMensaOfferingsIntentHandler(IntentHandlerWithMensaAndDate):
    """Handler for GetVegetarianMensaOfferingsIntent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """Overwritten."""
        return ask_utils.is_intent_name("GetVegetarianMensaOfferingsIntent")(
            handler_input
        ) or ask_utils.is_intent_name("GetVeganMensaOfferingsIntent")(handler_input)

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
        required_flag = NutritionFlag.VEGETARIAN
        if ask_utils.is_intent_name("GetVeganMensaOfferingsIntent")(handler_input):
            required_flag = NutritionFlag.VEGAN

        filtered_dishes = [
            menu
            for menu in mensa_offerings.menus
            if required_flag in menu.nutrition_flags
        ]
        if len(filtered_dishes) <= 0:
            speak_output = _("FILTERED_DISH_ANNOUNCEMENT_NO_DISHES").format(
                type=_(required_flag.value), mensa=_(mensa.mensaId), date=date
            )
            return handler_input.response_builder.speak(speak_output).response
        elif len(filtered_dishes) == 1:
            speak_output = _("FILTERED_DISH_ANNOUNCEMENT_ONE_DISH").format(
                type=_(required_flag.value),
                mensa=_(mensa.mensaId),
                date=date,
                dish=filtered_dishes[0].generate_full_announcement(_),
            )
            return handler_input.response_builder.speak(speak_output).response
        else:
            speak_output = _("FILTERED_DISH_ANNOUNCEMENT_MULTIPLE_DISHES").format(
                type=_(required_flag.value),
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
