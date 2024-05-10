import gettext

from ask_sdk_core.dispatch_components import AbstractRequestInterceptor
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.skill_builder import SkillBuilder

sb = SkillBuilder()


class LocalizationInterceptor(AbstractRequestInterceptor):
    """Request Interceptor for setting locale based on request."""

    def process(self, handler_input: HandlerInput) -> None:
        """Overwritten."""
        locale = (
            handler_input.request_envelope.request.locale
            if handler_input.request_envelope.request is not None
            and handler_input.request_envelope.request.locale is not None
            else "en-US"
        )

        i18n = gettext.translation(
            "skill", localedir="locales", languages=[locale], fallback=True
        )
        handler_input.attributes_manager.request_attributes["_"] = i18n.gettext


sb.add_global_request_interceptor(LocalizationInterceptor())
