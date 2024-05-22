import datetime
from typing import Optional, Set

from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import request_util

from src.data.mensas import Mensa


def get_mensas_from_slot(
    handler_input: HandlerInput, slot_name: str
) -> Optional[Set[Mensa]]:
    """Get the mensa from the slot.

    :param handler_input: The handler input (from the skill invocation)
    :param slot_name: The name of the slot
    :return: The mensa(s) that were found in the slot or None if no mensa was found
    """
    identified_slot_ids = _get_slot_ids_from_custom_slot(handler_input, slot_name)
    if identified_slot_ids is None:
        return None

    return {Mensa(mensa_id) for mensa_id in identified_slot_ids}


def get_date_from_slot(
    handler_input: HandlerInput, slot_name: str
) -> Optional[datetime.date]:
    """Get the date from the slot.

    If multiple values were specified, this function will return the first date that was found.
    :param handler_input: The handler input (from the skill invocation)
    :param slot_name: The name of the slot
    :return: The date that was found in the slot or None if no date was found
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

    parsed_date = datetime.datetime.strptime(date_value, "%Y-%m-%d")
    return parsed_date.date()


def _get_slot_ids_from_custom_slot(
    handler_input: HandlerInput, slot_name: str
) -> Optional[Set[str]]:
    """Get the slot IDs from the custom slot.

    :param handler_input: The handler input (from the skill invocation)
    :param slot_name: The name of the slot
    :return: The slot IDs that were found in the slot or None if no slot ID was found
    """
    slot_value = request_util.get_slot_value_v2(handler_input, slot_name)
    if slot_value is None:
        return None

    simple_slot_values = request_util.get_simple_slot_values(slot_value)
    if simple_slot_values is None:
        return None

    result_id_set: Set[str] = set()
    for simple_slot_value in simple_slot_values:
        slot_resolutions = simple_slot_value.resolutions
        if (
            slot_resolutions is None
            or slot_resolutions.resolutions_per_authority is None
        ):
            continue

        for resolution in slot_resolutions.resolutions_per_authority:
            if resolution.values is None:
                continue

            for value in resolution.values:
                if value.value is None or value.value.id is None:
                    continue

                resolution_id = value.value.id
                result_id_set.add(resolution_id)

    return result_id_set
