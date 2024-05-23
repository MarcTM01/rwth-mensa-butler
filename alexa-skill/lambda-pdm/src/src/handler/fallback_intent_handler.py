from typing import Callable, cast

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response


class FallbackIntentHandler(AbstractRequestHandler):
    """A fallback handler for all unhandled intents."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """Overwritten."""
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        """Overwritten."""
        _ = cast(
            Callable[[str], str],
            handler_input.attributes_manager.request_attributes["_"],
        )
        speak_output = _("FALLBACK_MESSAGE")

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )
