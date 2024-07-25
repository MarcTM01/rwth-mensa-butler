"""Defines handler for Skill Launch.

The launch intent is activated when a user opens the skill
(e.g., via 'Alexa, open RWTH Mensa')
"""

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.handler.abstract.i18n_request_handler import I18nRequestHandler
from src.utils.localization import I18nFunction


class LaunchRequestHandler(I18nRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """Accepts all LaunchRequest objects."""
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle_i18n(self, handler_input: HandlerInput, i18n: I18nFunction) -> Response:
        """Responds with a generic introduction to the skill."""
        speak_output = i18n("LAUNCH_MESSAGE")

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .set_should_end_session(False)
            .response
        )
