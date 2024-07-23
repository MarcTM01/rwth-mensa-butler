import abc
import datetime
from typing import Tuple, Union

import holidays
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.data import dynamodb
from src.data.mensas import Mensa
from src.data.menu_model import MensaDayMenus
from src.handler.abstract.i18n_request_handler import I18nRequestHandler
from src.utils import alexa_slots
from src.utils.localization import I18nFunction


def _require_exactly_one_mensa_specified(
    handler_input: HandlerInput, i18n: I18nFunction
) -> Union[Response, Mensa]:
    mensas = alexa_slots.get_mensas_from_slot(handler_input, "mensa")
    if mensas is None or len(mensas) == 0:
        return handler_input.response_builder.speak(i18n("NO_MENSA_SPECIFIED")).response

    mensa = next(iter(mensas))
    return mensa


def _require_one_date_specified(
    handler_input: HandlerInput, i18n: I18nFunction
) -> Union[Response, datetime.date]:
    date = alexa_slots.get_date_from_slot(handler_input, "date")
    if date is None:
        return handler_input.response_builder.speak(i18n("NO_DATE_SPECIFIED")).response
    return date


def _speak_probable_reason_for_no_menu_data(
    handler_input: HandlerInput,
    mensa: Mensa,
    date: datetime.date,
    i18n: I18nFunction,
) -> Response:
    weekday = date.weekday()
    if weekday == 5 or weekday == 6:
        return handler_input.response_builder.speak(
            i18n("NO_MENU_DATA_FOR_WEEKEND").format(
                mensa=i18n(mensa.mensaId),
                date=date.isoformat(),
                weekday=i18n(f"DAY_{weekday}"),
            )
        ).response

    nrw_holidays = holidays.country_holidays("DE", state="NW", years=[date.year])
    if date in nrw_holidays:
        return handler_input.response_builder.speak(
            i18n("NO_MENU_DATA_FOR_PUBLIC_HOLIDAY").format(
                mensa=i18n(mensa.mensaId), date=date.isoformat()
            )
        ).response

    return handler_input.response_builder.speak(
        i18n("NO_MENU_DATA_FOR_DATE").format(i18n(mensa.mensaId), date.isoformat())
    ).response


def _retrieve_mensa_offerings(
    handler_input: HandlerInput,
    mensa: Mensa,
    date: datetime.date,
    i18n: I18nFunction,
) -> Union[Response, MensaDayMenus]:
    table = dynamodb.get_dynamodb_table()
    dynamodb_item_id = f"{mensa.mensaId};{i18n('LANG_ID')};{date.isoformat()}"
    get_response = table.get_item(Key={"MensaIdLanguageKeyDate": dynamodb_item_id})

    if "Item" not in get_response:
        return _speak_probable_reason_for_no_menu_data(handler_input, mensa, date, i18n)

    return MensaDayMenus.model_validate(get_response["Item"])


def _retrieve_user_inputs(
    handler_input: HandlerInput, i18n: I18nFunction
) -> Union[Response, Tuple[Mensa, datetime.date, MensaDayMenus]]:
    mensa_response_or_value = _require_exactly_one_mensa_specified(handler_input, i18n)
    if isinstance(mensa_response_or_value, Response):
        return mensa_response_or_value

    date_response_or_value = _require_one_date_specified(handler_input, i18n)
    if isinstance(date_response_or_value, Response):
        return date_response_or_value

    mensa_offerings = _retrieve_mensa_offerings(
        handler_input, mensa_response_or_value, date_response_or_value, i18n
    )
    if isinstance(mensa_offerings, Response):
        return mensa_offerings

    return mensa_response_or_value, date_response_or_value, mensa_offerings


class IntentHandlerWithMensaAndDate(I18nRequestHandler, abc.ABC):
    """A base class for intent handlers that require a mensa and a date."""

    @abc.abstractmethod
    def handle_with_mensa_and_date(
        self,
        handler_input: HandlerInput,
        mensa: Mensa,
        date: datetime.date,
        mensa_offerings: MensaDayMenus,
        i18n: I18nFunction,
    ) -> Response:
        """Handle the intent with a mensa and a date."""
        pass

    def handle_i18n(self, handler_input: HandlerInput, i18n: I18nFunction) -> Response:
        """Overwritten."""
        response = _retrieve_user_inputs(handler_input, i18n)
        if isinstance(response, Response):
            return response
        mensa, date, mensa_offerings = response

        return self.handle_with_mensa_and_date(
            handler_input, mensa, date, mensa_offerings, i18n
        )
