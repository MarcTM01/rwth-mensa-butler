import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler,
)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import request_util
from ask_sdk_model import Response
from data import dynamodb


class GetMensaOfferingsIntentHandler(AbstractRequestHandler):
    """Handler for GetMensaOfferingsIntent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_intent_name("GetMensaOfferingsIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        mensa_id = request_util.get_slot(handler_input, "mensa").resolutions.resolutions_per_authority[0].values[
            0].value.id
        date = request_util.get_slot(handler_input, "date").value

        table = dynamodb.get_dynamodb_table()
        item = table.get_item(Key={"MensaIdLanguageKeyDate": "mensa-academica;en;2024-05-15"})

        speak_output = (
            f"Hello World! Let me check what's on the menu in {mensa_id} at {date} for you: {item}"
        )

        return handler_input.response_builder.speak(speak_output).response
