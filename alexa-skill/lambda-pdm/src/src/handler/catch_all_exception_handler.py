"""Defines a Catch-All Exception handler."""

import logging
from typing import cast

from ask_sdk_core.dispatch_components import (
    AbstractExceptionHandler,
)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.utils.localization import I18nFunction

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Captures syntax or routing errors.

    Generic error handling to capture any syntax or routing errors.
    If you receive an error stating the request handler chain is not found,
    you have not implemented a handler for the intent being invoked or included
    it in the skill builder below.
    """

    def can_handle(self, handler_input: HandlerInput, exception: Exception) -> bool:  # noqa: ARG002
        """Accepts anything."""
        return True

    def handle(self, handler_input: HandlerInput, exception: Exception) -> Response:
        """Informs the user about the failure."""
        logger.error(exception, exc_info=True)

        i18n = cast(
            I18nFunction,
            handler_input.attributes_manager.request_attributes["_"],
        )
        speak_output = i18n("ERROR_MESSAGE")

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )
