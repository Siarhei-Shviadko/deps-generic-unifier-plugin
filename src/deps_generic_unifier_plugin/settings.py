from pydantic import Field
from pydantic_settings import BaseSettings

from deps_generic_unifier_plugin.extras.settings import ServiceInfoSettings


class Settings(BaseSettings):
    env: str = Field("development")
    info: ServiceInfoSettings = ServiceInfoSettings()  # noqa: WPS110
    logger_level: str = Field("INFO", validation_alias="LOG_LEVEL")
    instrumentation_enabled: bool = Field(False)
