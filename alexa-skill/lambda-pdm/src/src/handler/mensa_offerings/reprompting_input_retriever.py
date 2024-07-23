import dataclasses
import datetime
from typing import Optional, Union

from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.data.dish_type_filter import DishTypeFilter
from src.data.mensas import Mensa
from src.utils import alexa_slots
from src.utils.localization import I18nFunction

DATE_SERIALIZATION_FORMAT = "%Y-%m-%d"


@dataclasses.dataclass
class MensaOfferingsParameters:
    mensa: Mensa
    date: datetime.date
    dish_type_filter: Optional[DishTypeFilter] = None


class MensaOfferingsParameterBuilder:
    mensa: Optional[Mensa] = None
    date: Optional[datetime.date] = None
    dish_type_filter: Optional[DishTypeFilter] = None

    def fill_from_attributes(self, handler_input: HandlerInput):
        attrs = handler_input.attributes_manager.session_attributes
        assert attrs is not None
        if "mensa_id" in attrs:
            self.mensa = Mensa(attrs["mensa_id"])
        if "date" in attrs:
            self.date = datetime.datetime.strptime(
                attrs["date"], DATE_SERIALIZATION_FORMAT
            ).date()
        if "dish_type_filter_id" in attrs:
            self.dish_type_filter = DishTypeFilter(attrs["dish_type_filter_id"])

    def save_to_attributes(self, handler_input: HandlerInput):
        attrs = handler_input.attributes_manager.session_attributes
        assert attrs is not None
        if self.mensa is not None:
            attrs["mensa_id"] = self.mensa.mensaId
        if self.date is not None:
            attrs["date"] = datetime.date.strftime(self.date, DATE_SERIALIZATION_FORMAT)
        if self.dish_type_filter is not None:
            attrs["dish_type_filter_id"] = self.dish_type_filter.name

    def fill_from_slots(self, handler_input: HandlerInput):
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
    ) -> Union[MensaOfferingsParameters, Response]:
        if self.mensa is None:
            msg = i18n("REPROMPT_FOR_MENSA")
            return handler_input.response_builder.speak(msg).ask(msg).response
        if self.date is None:
            msg = i18n("REPROMPT_FOR_DATE")
            return handler_input.response_builder.speak(msg).ask(msg).response
        return MensaOfferingsParameters(
            mensa=self.mensa, date=self.date, dish_type_filter=self.dish_type_filter
        )


def retrieve_get_mensa_offerings_parameters(
    handler_input: HandlerInput, i18n: I18nFunction
) -> Union[MensaOfferingsParameters, Response]:
    builder = MensaOfferingsParameterBuilder()

    builder.fill_from_attributes(handler_input)
    builder.fill_from_slots(handler_input)
    builder.save_to_attributes(handler_input)

    return builder.get_or_reprompt(handler_input, i18n)
