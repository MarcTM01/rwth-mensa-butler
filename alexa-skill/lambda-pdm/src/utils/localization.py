from typing import Callable, Iterable


def build_localized_list(i18n: Callable[[str], str], items: Iterable[str]) -> str:
    """Build a localized list.

    :param i18n: The translation function
    :param items: The items to list
    :return: The localized list
    """
    item_list = list(items)
    if len(item_list) == 0:
        return i18n("EMPTY_LIST")

    if len(item_list) == 1:
        return item_list[0]

    return i18n("LIST_SEPERATOR").join(item_list[:-1]) + i18n("LIST_CONJUNCTION") + item_list[-1]
