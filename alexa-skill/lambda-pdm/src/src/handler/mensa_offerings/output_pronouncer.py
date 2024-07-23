import datetime

from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from src.data.dish_type_filter import DishTypeFilter
from src.data.mensas import Mensa
from src.data.menu_model import DishType, MensaDayMenus
from src.utils import localization
from src.utils.localization import I18nFunction


def _speak_classical_and_vegetarian_dishes(
    i18n: I18nFunction, mensa_offerings: MensaDayMenus
) -> str:
    veggie_dish = mensa_offerings.get_menus_by_type(DishType.VEGETARIAN)
    classical_dish = mensa_offerings.get_menus_by_type(DishType.CLASSICS)

    speak_output = ""
    if len(veggie_dish) > 0:
        speak_output += veggie_dish[0].generate_full_announcement(i18n) + ". "
    if len(classical_dish) > 0:
        speak_output += classical_dish[0].generate_full_announcement(i18n) + "."

    return speak_output


def _speak_summary_about_additional_dishes(
    i18n: I18nFunction, mensa_offerings: MensaDayMenus
) -> str:
    additional_dishes = [
        menu
        for menu in mensa_offerings.menus
        if menu.dish_type not in {DishType.CLASSICS, DishType.VEGETARIAN}
    ]
    additional_dish_names = set([menu.name for menu in additional_dishes])
    if len(additional_dishes) <= 0:
        return ""

    dish_type_announcement = localization.build_localized_list(
        i18n, additional_dish_names, conjunction=False
    )

    if len(additional_dishes) == 1:
        return i18n("ONE_ADDITIONAL_DISH").format(dish_type_announcement)

    return i18n("NUMBER_OF_ADDITIONAL_DISHES").format(
        len(additional_dishes), dish_type_announcement
    )


def speak_standard_dish_types(
    handler_input: HandlerInput,
    mensa: Mensa,
    date: datetime.date,
    mensa_offerings: MensaDayMenus,
    i18n: I18nFunction,
) -> Response:
    speak_output = i18n("DISH_ANNOUNCEMENT_PREFIX").format(
        mensa=i18n(mensa.mensaId), date=date.isoformat()
    )
    speak_output += " " + _speak_classical_and_vegetarian_dishes(i18n, mensa_offerings)
    speak_output += " " + mensa_offerings.generate_extras_announcement(i18n)
    speak_output += " " + _speak_summary_about_additional_dishes(i18n, mensa_offerings)

    return (
        handler_input.response_builder.speak(speak_output)
        .set_should_end_session(True)
        .response
    )


def speak_filtered_dishes(
    handler_input: HandlerInput,
    mensa: Mensa,
    date: datetime.date,
    mensa_offerings: MensaDayMenus,
    dish_type_filter: DishTypeFilter,
    i18n: I18nFunction,
) -> Response:
    filtered_dishes = [
        menu for menu in mensa_offerings.menus if dish_type_filter.matches(menu)
    ]
    if len(filtered_dishes) <= 0:
        speak_output = i18n("FILTERED_DISH_ANNOUNCEMENT_NO_DISHES").format(
            type=i18n(f"FILTER_{dish_type_filter.value}_PLURAL"),
            mensa=i18n(mensa.mensaId),
            date=date,
        )
        return handler_input.response_builder.speak(speak_output).response
    elif len(filtered_dishes) == 1:
        speak_output = i18n("FILTERED_DISH_ANNOUNCEMENT_ONE_DISH").format(
            type=i18n(f"FILTER_{dish_type_filter.value}_SINGLE"),
            mensa=i18n(mensa.mensaId),
            date=date,
            dish=filtered_dishes[0].generate_full_announcement(i18n),
        )
        return handler_input.response_builder.speak(speak_output).response
    else:
        speak_output = i18n("FILTERED_DISH_ANNOUNCEMENT_MULTIPLE_DISHES").format(
            type=i18n(f"FILTER_{dish_type_filter.value}_PLURAL"),
            mensa=i18n(mensa.mensaId),
            date=date,
            num=len(filtered_dishes),
            dishes=". ".join(
                map(
                    lambda dish: dish.generate_full_announcement(i18n),
                    filtered_dishes,
                )
            ),
        )
        return (
            handler_input.response_builder.speak(speak_output)
            .set_should_end_session(True)
            .response
        )
