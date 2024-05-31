import logging

from ask_sdk_core.skill_builder import SkillBuilder

from src.handler.cancel_intent_handler import (
    CancelOrStopIntentHandler,
)
from src.handler.catch_all_exception_handler import (
    CatchAllExceptionHandler,
)
from src.handler.fallback_intent_handler import FallbackIntentHandler
from src.handler.get_filtered_mensa_offerings_intent_handler import (
    GetFilteredMensaOfferingsIntentHandler,
)
from src.handler.get_mensa_offerings_intent_handler import (
    GetMensaOfferingsIntentHandler,
)
from src.handler.help_intent_handler import (
    HelpIntentHandler,
)
from src.handler.launch_request_handler import (
    LaunchRequestHandler,
)
from src.handler.session_ended_request_handler import (
    SessionEndedRequestHandler,
)
from src.interceptors.localization_interceptor import LocalizationInterceptor

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sb = SkillBuilder()
sb.add_global_request_interceptor(LocalizationInterceptor())

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler())

sb.add_request_handler(GetFilteredMensaOfferingsIntentHandler())
sb.add_request_handler(GetMensaOfferingsIntentHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
