"""Defines the central intent handler for requesting mensa information."""

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.handler.abstract.i18n_request_handler import I18nRequestHandler
from src.handler.mensa_offerings import (
    data_retriever,
    output_pronouncer,
    reprompting_input_retriever,
)
from src.utils.localization import I18nFunction


class GetMensaOfferingsIntentHandler(I18nRequestHandler):
    """Handler for GetMensaOfferingsIntent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """Accepts all intents related to requesting menu data."""
        return (
            ask_utils.is_intent_name("GetMensaOfferingsIntent")(handler_input)
            or ask_utils.is_intent_name("SpecifyMensaIntent")(handler_input)
            or ask_utils.is_intent_name("SpecifyDateIntent")(handler_input)
        )

    def handle_i18n(self, handler_input: HandlerInput, i18n: I18nFunction) -> Response:
        """Answers the users queries regarding the menu data.

        When the stored request information (mensa, date, filters)
        is completed through this request, the mensa information is
        presented to the user

        When the stored request information is incomplete,
        the user is prompted for additional information.
        """
        parameters = (
            reprompting_input_retriever.retrieve_get_mensa_offerings_parameters(
                handler_input, i18n
            )
        )
        if isinstance(parameters, Response):
            return parameters

        menu_data = data_retriever.retrieve_mensa_offerings_or_speak_not_available(
            handler_input=handler_input,
            mensa=parameters.mensa,
            date=parameters.date,
            i18n=i18n,
        )
        if isinstance(menu_data, Response):
            return menu_data

        if parameters.dish_type_filter is None:
            return output_pronouncer.speak_standard_dish_types(
                handler_input=handler_input,
                mensa=parameters.mensa,
                date=parameters.date,
                i18n=i18n,
                mensa_offerings=menu_data,
            )
        return output_pronouncer.speak_filtered_dishes(
            handler_input=handler_input,
            mensa=parameters.mensa,
            date=parameters.date,
            dish_type_filter=parameters.dish_type_filter,
            i18n=i18n,
            mensa_offerings=menu_data,
        )
