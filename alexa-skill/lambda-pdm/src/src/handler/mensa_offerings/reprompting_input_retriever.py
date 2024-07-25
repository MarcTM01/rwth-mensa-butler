"""Handles obtaining all information from the user required to fulfil the request."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ask_sdk_core.handler_input import HandlerInput
    from ask_sdk_model import Response

    from src.utils.localization import I18nFunction

import dataclasses
import datetime

from src.data.dish_type_filter import DishTypeFilter
from src.data.mensas import Mensa
from src.utils import alexa_slots

DATE_SERIALIZATION_FORMAT = "%Y-%m-%d"


@dataclasses.dataclass
class MensaOfferingsParameters:
    """Defines all parameters that are part of a users request.

    Attributes:
        mensa: The mensa to query information about
        date: The date to query information about
        dish_type_filter:
            An optional filter for the kind of dishes the user is interested in
    """

    mensa: Mensa
    date: datetime.date
    dish_type_filter: DishTypeFilter | None = None


class MensaOfferingsParameterBuilder:
    """A builder for all parameters of a users requests.

    Allows retrieving and storing data in the Alexa Session Store
    to gradually build a complete model by re-prompting the user.
    """

    mensa: Mensa | None = None
    date: datetime.date | None = None
    dish_type_filter: DishTypeFilter | None = None

    def fill_from_attributes(self, handler_input: HandlerInput) -> None:
        """Loads any available data from session attributes."""
        attrs = handler_input.attributes_manager.session_attributes
        assert attrs is not None
        if "mensa_id" in attrs:
            self.mensa = Mensa(attrs["mensa_id"])
        if "date" in attrs:
            self.date = (
                datetime.datetime.strptime(attrs["date"], DATE_SERIALIZATION_FORMAT)
                .astimezone(datetime.timezone.utc)
                .date()
            )
        if "dish_type_filter_id" in attrs:
            self.dish_type_filter = DishTypeFilter(attrs["dish_type_filter_id"])

    def save_to_attributes(self, handler_input: HandlerInput) -> None:
        """Stores all data to session attributes."""
        attrs = handler_input.attributes_manager.session_attributes
        assert attrs is not None
        if self.mensa is not None:
            attrs["mensa_id"] = self.mensa.mensa_id
        if self.date is not None:
            attrs["date"] = datetime.date.strftime(self.date, DATE_SERIALIZATION_FORMAT)
        if self.dish_type_filter is not None:
            attrs["dish_type_filter_id"] = self.dish_type_filter.name

    def fill_from_slots(self, handler_input: HandlerInput) -> None:
        """Loads all available data from slots."""
        mensas = alexa_slots.get_mensas_from_slot(handler_input, "mensa")
        if mensas is not None and len(mensas) == 1:
            self.mensa = next(iter(mensas))

        date = alexa_slots.get_date_from_slot(handler_input, "date")
        if date is not None:
            self.date = date

        dish_type_filters = alexa_slots.get_dish_type_filters_from_slot(
            handler_input, "dishType"
        )
        if dish_type_filters is not None and len(dish_type_filters) == 1:
            self.dish_type_filter = next(iter(dish_type_filters))

    def get_or_reprompt(
        self, handler_input: HandlerInput, i18n: I18nFunction
    ) -> MensaOfferingsParameters | Response:
        """Builds the model. Prompts the user for missing input."""
        if self.mensa is None:
            msg = i18n("REPROMPT_FOR_MENSA")
            return (
                handler_input.response_builder.speak(msg)
                .ask(msg)
                .set_should_end_session(False)
                .response
            )
        if self.date is None:
            msg = i18n("REPROMPT_FOR_DATE")
            return (
                handler_input.response_builder.speak(msg)
                .ask(msg)
                .set_should_end_session(False)
                .response
            )
        return MensaOfferingsParameters(
            mensa=self.mensa, date=self.date, dish_type_filter=self.dish_type_filter
        )


def retrieve_get_mensa_offerings_parameters(
    handler_input: HandlerInput, i18n: I18nFunction
) -> MensaOfferingsParameters | Response:
    """Handle the data-retrival stage of the question-answering pipeline.

    Returns:
        If all data is provided (either in the attribute store or the prompt slots),
         return them.
        If required data is missing,
         return a response re-prompting for that information.
    """
    builder = MensaOfferingsParameterBuilder()

    builder.fill_from_attributes(handler_input)
    builder.fill_from_slots(handler_input)
    builder.save_to_attributes(handler_input)

    return builder.get_or_reprompt(handler_input, i18n)
