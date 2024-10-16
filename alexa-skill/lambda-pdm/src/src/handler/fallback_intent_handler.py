"""Defines handler for Fallback Intent.

The fallback intent is called, when there is no other matching intend
in this skill.
"""

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.handler.abstract.i18n_request_handler import I18nRequestHandler
from src.utils.localization import I18nFunction


class FallbackIntentHandler(I18nRequestHandler):
    """A fallback handler for all unhandled intents."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """Accepts all FallbackIntent objects."""
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle_i18n(self, handler_input: HandlerInput, i18n: I18nFunction) -> Response:
        """Informs the user about the failure.

        Suggests to go to GitHub for filing an issue.
        """
        speak_output = i18n("FALLBACK_MESSAGE")

        return handler_input.response_builder.speak(speak_output).response
