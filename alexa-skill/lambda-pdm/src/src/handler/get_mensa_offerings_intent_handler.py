import datetime
from typing import Callable, Tuple, Union, cast

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler,
)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.data import dynamodb
from src.data.mensas import Mensa
from src.data.menu_model import MensaDayMenus
from src.utils import alexa_slots, localization


def _require_exactly_one_mensa_specified(
        handler_input: HandlerInput,
) -> Union[Response, Mensa]:
    _ = cast(
        Callable[[str], str],
        handler_input.attributes_manager.request_attributes["_"],
    )

    mensas = alexa_slots.get_mensas_from_slot(handler_input, "mensa")
    if mensas is None or len(mensas) == 0:
        return handler_input.response_builder.speak(
            _("NO_MENSA_SPECIFIED")
        ).response

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
        return handler_input.response_builder.speak(
            _("NO_DATE_SPECIFIED")
        ).response
    return date


def _retrieve_mensa_offerings(handler_input: HandlerInput, mensa: Mensa, date: datetime.date) -> Union[
    Response, MensaDayMenus]:
    _ = cast(
        Callable[[str], str],
        handler_input.attributes_manager.request_attributes["_"],
    )
    table = dynamodb.get_dynamodb_table()
    dynamodb_item_id = f"{mensa.mensaId};en;{date.isoformat()}"
    get_response = table.get_item(Key={"MensaIdLanguageKeyDate": dynamodb_item_id})

    if "Item" not in get_response:
        return handler_input.response_builder.speak(
            _("NO_MENU_DATA_FOR_DATE").format(_(mensa.mensaId), date.isoformat())
        ).response

    return MensaDayMenus.model_validate(get_response["Item"])


class GetMensaOfferingsIntentHandler(AbstractRequestHandler):
    """Handler for GetMensaOfferingsIntent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """Overwritten."""
        return ask_utils.is_intent_name("GetMensaOfferingsIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        """Overwritten."""
        _ = cast(
            Callable[[str], str],
            handler_input.attributes_manager.request_attributes["_"],
        )

        mensa_response_or_value = _require_exactly_one_mensa_specified(handler_input)
        if isinstance(mensa_response_or_value, Response):
            return mensa_response_or_value

        date_response_or_value = _require_one_date_specified(handler_input)
        if isinstance(date_response_or_value, Response):
            return date_response_or_value

        mensa_offerings = _retrieve_mensa_offerings(handler_input, mensa_response_or_value, date_response_or_value)
        if isinstance(mensa_offerings, Response):
            return mensa_offerings

        speak_output = f"There are a total of {len(mensa_offerings.menus)} menus available for {mensa_response_or_value.mensaId} on {date_response_or_value.isoformat()}."

        return handler_input.response_builder.speak(speak_output).response
