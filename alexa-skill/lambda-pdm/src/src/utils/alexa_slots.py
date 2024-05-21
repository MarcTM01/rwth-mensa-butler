from typing import Optional, Set

from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import request_util

from src.data.mensas import Mensa


def get_mensas_from_slot(handler_input: HandlerInput, slot_name: str) -> Optional[Set[Mensa]]:
    """Get the mensa from the slot.

    :param handler_input: The handler input (from the skill invocation)
    :param slot_name: The name of the slot
    :return: The mensa(s) that were found in the slot or None if no mensa was found
    """
    mensa_slot_value = request_util.get_slot_value_v2(handler_input, slot_name)
    if mensa_slot_value is None:
        return None

    mensa_simple_slot_values = request_util.get_simple_slot_values(mensa_slot_value)
    if mensa_simple_slot_values is None:
        return None

    result_list: Set[Mensa] = set()
    for mensa_slot_simple_value in mensa_simple_slot_values:
        slot_resolutions = mensa_slot_simple_value.resolutions
        if slot_resolutions is None:
            continue

        for resolution in slot_resolutions.resolutions_per_authority:
            for value in resolution.values:
                mensa_id = value.value.id
                mensa = Mensa(mensa_id)
                result_list.add(mensa)

    if len(result_list) == 0:
        return None

    return result_list
