import datetime
from typing import Union

import holidays
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.data import dynamodb
from src.data.mensas import Mensa
from src.data.menu_model import MensaDayMenus
from src.utils.localization import I18nFunction


def _speak_probable_reason_for_no_menu_data(
    handler_input: HandlerInput,
    mensa: Mensa,
    date: datetime.date,
    i18n: I18nFunction,
) -> Response:
    weekday = date.weekday()
    if weekday == 5 or weekday == 6:
        return handler_input.response_builder.speak(
            i18n("NO_MENU_DATA_FOR_WEEKEND").format(
                mensa=i18n(mensa.mensaId),
                date=date.isoformat(),
                weekday=i18n(f"DAY_{weekday}"),
            )
        ).response

    nrw_holidays = holidays.country_holidays("DE", state="NW", years=[date.year])
    if date in nrw_holidays:
        return handler_input.response_builder.speak(
            i18n("NO_MENU_DATA_FOR_PUBLIC_HOLIDAY").format(
                mensa=i18n(mensa.mensaId), date=date.isoformat()
            )
        ).response

    return handler_input.response_builder.speak(
        i18n("NO_MENU_DATA_FOR_DATE").format(i18n(mensa.mensaId), date.isoformat())
    ).response


def retrieve_mensa_offerings_or_speak_not_available(
    handler_input: HandlerInput,
    mensa: Mensa,
    date: datetime.date,
    i18n: I18nFunction,
) -> Union[Response, MensaDayMenus]:
    table = dynamodb.get_dynamodb_table()
    dynamodb_item_id = f"{mensa.mensaId};{i18n('LANG_ID')};{date.isoformat()}"
    get_response = table.get_item(Key={"MensaIdLanguageKeyDate": dynamodb_item_id})

    if "Item" not in get_response:
        return _speak_probable_reason_for_no_menu_data(handler_input, mensa, date, i18n)

    menu = MensaDayMenus.model_validate(get_response["Item"])
    menu.menus = [x for x in menu.menus if not x.empty]
    return menu
