import logging

from ask_sdk_core.skill_builder import SkillBuilder
from handler.cancel_intent_handler import (
    CancelOrStopIntentHandler,
)
from handler.catch_all_exception_handler import (
    CatchAllExceptionHandler,
)
from handler.get_mensa_offerings_intent_handler import GetMensaOfferingsIntentHandler
from handler.help_intent_handler import (
    HelpIntentHandler,
)
from handler.launch_request_handler import (
    LaunchRequestHandler,
)
from handler.localization_interceptor import LocalizationInterceptor
from handler.session_ended_request_handler import (
    SessionEndedRequestHandler,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sb = SkillBuilder()
sb.add_global_request_interceptor(LocalizationInterceptor())

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetMensaOfferingsIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
