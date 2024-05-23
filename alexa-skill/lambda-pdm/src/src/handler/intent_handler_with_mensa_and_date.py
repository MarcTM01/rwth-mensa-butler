import abc
import datetime
from typing import Callable, Tuple, Union, cast

import holidays
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler,
)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.data import dynamodb
from src.data.mensas import Mensa
from src.data.menu_model import MensaDayMenus
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
    _ = cast(
        I18nFunction,
        handler_input.attributes_manager.request_attributes["_"],
    )

    table = dynamodb.get_dynamodb_table()
    dynamodb_item_id = f"{mensa.mensaId};{_('LANG_ID')};{date.isoformat()}"
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


class IntentHandlerWithMensaAndDate(AbstractRequestHandler, abc.ABC):
    """A base class for intent handlers that require a mensa and a date."""

    @abc.abstractmethod
    def handle_with_mensa_and_date(
        self,
        handler_input: HandlerInput,
        mensa: Mensa,
        date: datetime.date,
        mensa_offerings: MensaDayMenus,
    ) -> Response:
        """Handle the intent with a mensa and a date."""
        pass

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

        return self.handle_with_mensa_and_date(
            handler_input, mensa, date, mensa_offerings
        )
