import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler,
)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import request_util
from ask_sdk_model import Response


class GetMensaOfferingsIntentHandler(AbstractRequestHandler):
    """Handler for GetMensaOfferingsIntent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_intent_name("GetMensaOfferingsIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        mensa_name = request_util.get_slot(handler_input, "mensa")
        speak_output = (
            f"Hello World! Let me check what's on the menu in {mensa_name} for you."
        )

        return handler_input.response_builder.speak(speak_output).response
