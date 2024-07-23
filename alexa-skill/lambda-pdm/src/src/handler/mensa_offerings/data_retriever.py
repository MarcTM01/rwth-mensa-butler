"""Module for retrieving the information the user requested."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import datetime

    from ask_sdk_core.handler_input import HandlerInput
    from ask_sdk_model import Response

    from src.data.mensas import Mensa
    from src.utils.localization import I18nFunction

import holidays

from src.data import dynamodb
from src.data.menu_model import MensaDayMenus

WEEKDAY_SATURDAY = 5
WEEKDAY_SUNDAY = 6


def _speak_probable_reason_for_no_menu_data(
    handler_input: HandlerInput,
    mensa: Mensa,
    date: datetime.date,
    i18n: I18nFunction,
) -> Response:
    weekday = date.weekday()
    if weekday == WEEKDAY_SATURDAY or weekday == WEEKDAY_SUNDAY:  # noqa PLR1714
        return handler_input.response_builder.speak(
            i18n("NO_MENU_DATA_FOR_WEEKEND").format(
                mensa=i18n(mensa.mensa_id),
                date=date.isoformat(),
                weekday=i18n(f"DAY_{weekday}"),
            )
        ).response

    nrw_holidays = holidays.country_holidays("DE", state="NW", years=[date.year])
    if date in nrw_holidays:
        return handler_input.response_builder.speak(
            i18n("NO_MENU_DATA_FOR_PUBLIC_HOLIDAY").format(
                mensa=i18n(mensa.mensa_id), date=date.isoformat()
            )
        ).response

    return handler_input.response_builder.speak(
        i18n("NO_MENU_DATA_FOR_DATE").format(i18n(mensa.mensa_id), date.isoformat())
    ).response


def retrieve_mensa_offerings_or_speak_not_available(
    handler_input: HandlerInput,
    mensa: Mensa,
    date: datetime.date,
    i18n: I18nFunction,
) -> Response | MensaDayMenus:
    """Retrieves the requested information.

    Returns:
        The requested information, if available.
        An error message explaining potential reasons, if it is not.
    """
    table = dynamodb.get_dynamodb_table()
    dynamodb_item_id = f"{mensa.mensa_id};{i18n('LANG_ID')};{date.isoformat()}"
    get_response = table.get_item(Key={"MensaIdLanguageKeyDate": dynamodb_item_id})

    if "Item" not in get_response:
        return _speak_probable_reason_for_no_menu_data(handler_input, mensa, date, i18n)

    menu = MensaDayMenus.model_validate(get_response["Item"])
    menu.menus = [x for x in menu.menus if not x.empty]
    return menu
