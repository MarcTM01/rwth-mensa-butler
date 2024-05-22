from typing import Callable, Iterable

I18nFunction = Callable[[str], str]


def build_localized_list(
    i18n: I18nFunction, items: Iterable[str], conjunction: bool = True
) -> str:
    """Build a localized list.

    :param i18n: The translation function
    :param items: The items to list
    :param conjunction: Whether to use a conjunction or disjunction
    :return: The localized list
    """
    item_list = list(items)
    if len(item_list) == 0:
        return i18n("EMPTY_LIST")

    if len(item_list) == 1:
        return item_list[0]

    return (
        i18n("LIST_SEPERATOR").join(item_list[:-1])
        + i18n("LIST_CONJUNCTION" if conjunction else "LIST_DISJUNCTION")
        + item_list[-1]
    )