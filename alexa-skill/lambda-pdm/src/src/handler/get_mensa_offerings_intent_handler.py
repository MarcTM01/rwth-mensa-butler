import datetime
from typing import Callable, Tuple, Union, cast

import ask_sdk_core.utils as ask_utils
import holidays
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler,
)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.data import dynamodb
from src.data.mensas import Mensa
from src.data.menu_model import DishType, MensaDayMenus
from src.utils import alexa_slots, localization
from src.utils.localization import I18nFunction


def _require_exactly_one_mensa_specified(
        handler_input: HandlerInput,
) -> Union[Response, Mensa]:
    _ = cast(
        Callable[[str], str],
        handler_input.attributes_manager.request_attributes["_"],
    )

    mensas = alexa_slots.get_mensas_from_slot(handler_input, "mensa")
    if mensas is None or len(mensas) == 0:
        return handler_input.response_builder.speak(_("NO_MENSA_SPECIFIED")).response

    if len(mensas) != 1:
        mensa_names = map(lambda mensa_obj: _(mensa_obj.mensaId), mensas)
        return handler_input.response_builder.speak(
            _("MULTIPLE_MENSAS_SPECIFIED").format(
                localization.build_localized_list(_, mensa_names)
            )
        ).response

    mensa = next(iter(mensas))
    return mensa


def _require_one_date_specified(
        handler_input: HandlerInput,
) -> Union[Response, datetime.date]:
    _ = cast(
        Callable[[str], str],
        handler_input.attributes_manager.request_attributes["_"],
    )
    date = alexa_slots.get_date_from_slot(handler_input, "date")
    if date is None:
        return handler_input.response_builder.speak(_("NO_DATE_SPECIFIED")).response
    return date


def _speak_probable_reason_for_no_menu_data(
        handler_input: HandlerInput, mensa: Mensa, date: datetime.date
) -> Response:
    _ = cast(
        I18nFunction,
        handler_input.attributes_manager.request_attributes["_"],
    )

    weekday = date.weekday()
    if weekday == 5 or weekday == 6:
        return handler_input.response_builder.speak(
            _("NO_MENU_DATA_FOR_WEEKEND").format(
                mensa=_(mensa.mensaId),
                date=date.isoformat(),
                weekday=_(f"DAY_{weekday}"),
            )
        ).response

    nrw_holidays = holidays.country_holidays("DE", state="NW", years=[date.year])
    if date in nrw_holidays:
        return handler_input.response_builder.speak(
            _("NO_MENU_DATA_FOR_PUBLIC_HOLIDAY").format(
                mensa=_(mensa.mensaId), date=date.isoformat()
            )
        ).response

    return handler_input.response_builder.speak(
        _("NO_MENU_DATA_FOR_DATE").format(_(mensa.mensaId), date.isoformat())
    ).response


def _retrieve_mensa_offerings(
        handler_input: HandlerInput, mensa: Mensa, date: datetime.date
) -> Union[Response, MensaDayMenus]:
    table = dynamodb.get_dynamodb_table()
    dynamodb_item_id = f"{mensa.mensaId};en;{date.isoformat()}"
    get_response = table.get_item(Key={"MensaIdLanguageKeyDate": dynamodb_item_id})

    if "Item" not in get_response:
        return _speak_probable_reason_for_no_menu_data(handler_input, mensa, date)

    return MensaDayMenus.model_validate(get_response["Item"])


def _retrieve_user_inputs(
        handler_input: HandlerInput,
) -> Union[Response, Tuple[Mensa, datetime.date, MensaDayMenus]]:
    mensa_response_or_value = _require_exactly_one_mensa_specified(handler_input)
    if isinstance(mensa_response_or_value, Response):
        return mensa_response_or_value

    date_response_or_value = _require_one_date_specified(handler_input)
    if isinstance(date_response_or_value, Response):
        return date_response_or_value

    mensa_offerings = _retrieve_mensa_offerings(
        handler_input, mensa_response_or_value, date_response_or_value
    )
    if isinstance(mensa_offerings, Response):
        return mensa_offerings

    return mensa_response_or_value, date_response_or_value, mensa_offerings


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


class GetMensaOfferingsIntentHandler(AbstractRequestHandler):
    """Handler for GetMensaOfferingsIntent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """Overwritten."""
        return ask_utils.is_intent_name("GetMensaOfferingsIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        """Overwritten."""
        _ = cast(
            I18nFunction,
            handler_input.attributes_manager.request_attributes["_"],
        )

        response = _retrieve_user_inputs(handler_input)
        if isinstance(response, Response):
            return response
        mensa, date, mensa_offerings = response

        speak_output = _("DISH_ANNOUNCEMENT_PREFIX").format(
            mensa=_(mensa.mensaId), date=date.isoformat()
        )
        speak_output += " " + _speak_classical_and_vegetarian_dishes(_, mensa_offerings)
        speak_output += " " + mensa_offerings.generate_extras_announcement(_)
        speak_output += " " + _speak_summary_about_additional_dishes(_, mensa_offerings)

        return handler_input.response_builder.speak(speak_output).response
