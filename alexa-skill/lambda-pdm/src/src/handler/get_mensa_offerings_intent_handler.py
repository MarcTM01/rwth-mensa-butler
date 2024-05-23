import datetime
from typing import cast

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.data.mensas import Mensa
from src.data.menu_model import DishType, MensaDayMenus
from src.handler.intent_handler_with_mensa_and_date import IntentHandlerWithMensaAndDate
from src.utils import localization
from src.utils.localization import I18nFunction


def _speak_classical_and_vegetarian_dishes(
    _: I18nFunction, mensa_offerings: MensaDayMenus
) -> str:
    veggie_dish = mensa_offerings.get_menus_by_type(DishType.VEGETARIAN)
    classical_dish = mensa_offerings.get_menus_by_type(DishType.CLASSICS)

    speak_output = ""
    if len(veggie_dish) > 0:
        speak_output += veggie_dish[0].generate_full_announcement(_) + ". "
    if len(classical_dish) > 0:
        speak_output += classical_dish[0].generate_full_announcement(_) + "."

    return speak_output


def _speak_summary_about_additional_dishes(
    _: I18nFunction, mensa_offerings: MensaDayMenus
) -> str:
    additional_dishes = [
        menu
        for menu in mensa_offerings.menus
        if menu.dish_type not in {DishType.CLASSICS, DishType.VEGETARIAN}
    ]
    additional_dish_names = set([menu.name for menu in additional_dishes])
    if len(additional_dishes) <= 0:
        return ""

    dish_type_announcement = localization.build_localized_list(
        _, additional_dish_names, conjunction=False
    )

    if len(additional_dishes) == 1:
        return _("ONE_ADDITIONAL_DISH").format(dish_type_announcement)

    return _("NUMBER_OF_ADDITIONAL_DISHES").format(
        len(additional_dishes), dish_type_announcement
    )


class GetMensaOfferingsIntentHandler(IntentHandlerWithMensaAndDate):
    """Handler for GetMensaOfferingsIntent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """Overwritten."""
        return ask_utils.is_intent_name("GetMensaOfferingsIntent")(handler_input)

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

        speak_output = _("DISH_ANNOUNCEMENT_PREFIX").format(
            mensa=_(mensa.mensaId), date=date.isoformat()
        )
        speak_output += " " + _speak_classical_and_vegetarian_dishes(_, mensa_offerings)
        speak_output += " " + mensa_offerings.generate_extras_announcement(_)
        speak_output += " " + _speak_summary_about_additional_dishes(_, mensa_offerings)

        return handler_input.response_builder.speak(speak_output).response
