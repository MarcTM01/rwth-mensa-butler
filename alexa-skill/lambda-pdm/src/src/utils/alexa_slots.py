"""This module defines utility functions for dealing with Alexa Slots."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_core.utils import request_util

from src.data.dish_type_filter import DishTypeFilter
from src.data.mensas import Mensa


def _get_slot_ids_from_custom_slot(
    handler_input: HandlerInput, slot_name: str
) -> set[str] | None:
    """Get the slot IDs from the custom slot.

    Args:
        handler_input: The handler input from the skill invocation
        slot_name: The name of the slot

    Returns:
        The slot IDs that were found in the slot or None if no slot ID was found
    """
    slot_value = request_util.get_slot_value_v2(handler_input, slot_name)
    if slot_value is None:
        return None

    simple_slot_values = request_util.get_simple_slot_values(slot_value)
    if simple_slot_values is None:
        return None

    result_id_set: set[str] = set()
    for simple_slot_value in simple_slot_values:
        slot_resolutions = simple_slot_value.resolutions
        if (
            slot_resolutions is None
            or slot_resolutions.resolutions_per_authority is None
        ):
            continue

        for resolution in slot_resolutions.resolutions_per_authority:
            if resolution.values is None:  # noqa PD011
                continue

            for value in resolution.values:  # noqa PD011
                if value.value is None or value.value.id is None:
                    continue

                resolution_id = value.value.id
                result_id_set.add(resolution_id)

    return result_id_set


def get_dish_type_filters_from_slot(
    handler_input: HandlerInput, slot_name: str
) -> set[DishTypeFilter] | None:
    """Get the dish type filter from the slot.

    Args:
        handler_input: The handler input (from the skill invocation)
        slot_name: The name of the slot

    Returns:
        The dish type filter(s) that were found in the slot
        or None if no filter was found
    """
    identified_slot_ids = _get_slot_ids_from_custom_slot(handler_input, slot_name)
    if identified_slot_ids is None:
        return None

    return {DishTypeFilter(dish_type_id) for dish_type_id in identified_slot_ids}


def get_mensas_from_slot(
    handler_input: HandlerInput, slot_name: str
) -> set[Mensa] | None:
    """Get the mensa from the slot.

    Args:
        handler_input: The handler input (from the skill invocation)
        slot_name: The name of the slot

    Returns:
        The mensa(s) that were found in the slot or None if no mensa was found
    """
    identified_slot_ids = _get_slot_ids_from_custom_slot(handler_input, slot_name)
    if identified_slot_ids is None:
        return None

    return {Mensa(mensa_id) for mensa_id in identified_slot_ids}


def get_date_from_slot(
    handler_input: HandlerInput, slot_name: str
) -> datetime.date | None:
    """Get the date from the slot.

    If multiple values were specified, this function will return
    the first date that was found.

    Args:
        handler_input: The handler input from the skill invocation
        slot_name: The name of the slot

    Returns:
        The date that was found in the slot or None if no date was found
    """
    date_slot_value = request_util.get_slot_value_v2(handler_input, slot_name)
    if date_slot_value is None:
        return None

    date_slot_simple_values = request_util.get_simple_slot_values(date_slot_value)
    if date_slot_simple_values is None:
        return None

    if len(date_slot_simple_values) == 0:
        return None

    date_slot_simple_value = date_slot_simple_values[0]
    date_value = date_slot_simple_value.value
    if date_value is None:
        return None

    parsed_date = datetime.datetime.strptime(date_value, "%Y-%m-%d").astimezone(
        datetime.timezone.utc
    )
    return parsed_date.date()
