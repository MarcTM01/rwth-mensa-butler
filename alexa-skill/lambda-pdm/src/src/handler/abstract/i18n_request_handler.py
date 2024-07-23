import abc
from typing import cast

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.utils.localization import I18nFunction


class I18nRequestHandler(AbstractRequestHandler, abc.ABC):
    """A request handler that retrieves the i18n-mapping from attributes."""

    def handle(self, handler_input: HandlerInput) -> Response:
        """Forward request to handle_i18n."""
        i18n = cast(
            I18nFunction,
            handler_input.attributes_manager.request_attributes["_"],
        )
        return self.handle_i18n(handler_input, i18n)

    @abc.abstractmethod
    def handle_i18n(self, handler_input: HandlerInput, i18n: I18nFunction) -> Response:
        """Handle the request to produce a response."""
        pass
