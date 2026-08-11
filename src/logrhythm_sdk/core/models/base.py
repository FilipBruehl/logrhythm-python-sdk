"""Shared Pydantic model foundations for the SDK."""

from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator, AwareDatetime, BaseModel, ConfigDict

__all__ = ["InternalModel", "RequestModel", "ResponseModel", "SdkModel"]


def _normalize_to_utc(value: datetime) -> datetime:
    return value.astimezone(UTC)


type _UtcDatetime = Annotated[AwareDatetime, AfterValidator(_normalize_to_utc)]


class SdkModel(BaseModel):
    """Provide the common immutable validation policy for SDK models."""

    model_config = ConfigDict(
        frozen=True,
        validate_by_name=True,
        validate_by_alias=True,
    )


class RequestModel(SdkModel):
    """Reject unknown fields in outbound request data."""

    model_config = ConfigDict(extra="forbid")


class ResponseModel(SdkModel):
    """Allow and retain unknown fields in inbound response data."""

    model_config = ConfigDict(extra="allow")


class InternalModel(SdkModel):
    """Reject unknown fields in SDK-controlled internal data."""

    model_config = ConfigDict(extra="forbid")
