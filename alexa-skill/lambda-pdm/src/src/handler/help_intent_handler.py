"""Defines handler for Help Intent.

The help intent is raised when a user asks for help.
"""

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.handler.abstract.i18n_request_handler import I18nRequestHandler
from src.utils.localization import I18nFunction


class HelpIntentHandler(I18nRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """Accepts all HelpIntent objects."""
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle_i18n(self, handler_input: HandlerInput, i18n: I18nFunction) -> Response:
        """Responds with a help message informing users how to use this skill."""
        speak_output = i18n("HELP_MESSAGE")

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )
