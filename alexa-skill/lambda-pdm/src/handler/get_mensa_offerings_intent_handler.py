
from typing import Callable, Tuple, Union, cast

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler,
)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from data import dynamodb
from data.mensas import Mensa
from utils import alexa_slots, localization


def _extract_user_inputs(handler_input: HandlerInput) -> Union[
    Tuple[Response, None], Tuple[None, Mensa]]:
    _ = cast(
        Callable[[str], str],
        handler_input.attributes_manager.request_attributes["_"],
    )

    mensas = alexa_slots.get_mensas_from_slot(handler_input, "mensa")
    if mensas is None:
        return handler_input.response_builder.speak(_("NO_MENSA_SPECIFIED")).response, None

    if len(mensas) != 1:
        mensa_names = map(lambda mensa_obj: _(mensa_obj.mensaId), mensas)
        return handler_input.response_builder.speak(
            _("MULTIPLE_MENSAS_SPECIFIED") % localization.build_localized_list(_, mensa_names)
        ).response, None

    mensa = next(iter(mensas))
    return None, mensa


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

        response, mensa = _extract_user_inputs(handler_input)
        if response is not None:
            return response

        table = dynamodb.get_dynamodb_table()
        item = table.get_item(Key={"MensaIdLanguageKeyDate": "mensa-academica;en;2024-05-15"})

        speak_output = (
            f"Hello World! Let me check what's on the menu in {_(mensa.mensaId)} for you: {item}"
        )

        return handler_input.response_builder.speak(speak_output).response
