
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.handler.abstract.i18n_request_handler import I18nRequestHandler
from src.utils.localization import I18nFunction


class CancelOrStopIntentHandler(I18nRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """Overwritten."""
        return ask_utils.is_intent_name("AMAZON.CancelIntent")(
            handler_input
        ) or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle_i18n(self, handler_input: HandlerInput, i18n: I18nFunction) -> Response:
        """Overwritten."""
        speak_output = i18n("CANCEL_MESSAGE")

        return handler_input.response_builder.speak(speak_output).response
