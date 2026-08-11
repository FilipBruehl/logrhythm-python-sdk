"""Tests for the shared Pydantic model foundations (SPEC-008)."""

from datetime import UTC, datetime, timedelta, timezone
from enum import Enum

import pytest
from pydantic import BaseModel, Field, ValidationError

from logrhythm_sdk.core import models
from logrhythm_sdk.core.models import InternalModel, RequestModel, ResponseModel, SdkModel
from logrhythm_sdk.core.models.base import _UtcDatetime
from logrhythm_sdk.exceptions import RequestValidationError, ResponseValidationError


class _AliasedModel(SdkModel):
    alarm_rule_id: int = Field(alias="alarmRuleID")


class _PlainModel(SdkModel):
    alarm_rule_id: int


class _Request(RequestModel):
    value: int


class _Response(ResponseModel):
    alarm_rule_id: int = Field(alias="alarmRuleID")


class _Internal(InternalModel):
    value: int


class _State(Enum):
    ACTIVE = "active"


class _EnumModel(SdkModel):
    state: _State


class _DatetimeModel(SdkModel):
    occurred_at: _UtcDatetime


def test_direct_model_hierarchy() -> None:
    assert SdkModel.__bases__ == (BaseModel,)
    assert RequestModel.__bases__ == (SdkModel,)
    assert ResponseModel.__bases__ == (SdkModel,)
    assert InternalModel.__bases__ == (SdkModel,)


def test_models_facade_exports_only_the_foundation_classes() -> None:
    assert set(models.__all__) == {"InternalModel", "RequestModel", "ResponseModel", "SdkModel"}
    assert models.InternalModel is InternalModel
    assert models.RequestModel is RequestModel
    assert models.ResponseModel is ResponseModel
    assert models.SdkModel is SdkModel


@pytest.mark.parametrize(
    "model",
    [
        _AliasedModel(alarm_rule_id=123),
        _AliasedModel(alarmRuleID=123),
        _AliasedModel.model_validate({"alarm_rule_id": 123}),
        _AliasedModel.model_validate({"alarmRuleID": 123}),
    ],
)
def test_explicit_alias_accepts_python_name_and_alias(model: _AliasedModel) -> None:
    assert model.alarm_rule_id == 123


def test_dump_uses_python_names_by_default_and_aliases_on_request() -> None:
    model = _AliasedModel(alarmRuleID=123)

    assert model.model_dump() == {"alarm_rule_id": 123}
    assert model.model_dump(by_alias=True) == {"alarmRuleID": 123}


def test_no_alias_is_generated_implicitly() -> None:
    with pytest.raises(ValidationError):
        _PlainModel.model_validate({"alarmRuleID": 123})


def test_request_accepts_and_validates_known_fields() -> None:
    assert _Request(value="123").value == 123


def test_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        _Request(value=1, unknown_field=True)


def test_request_rejects_invalid_known_fields() -> None:
    with pytest.raises(ValidationError):
        _Request(value="not-an-integer")


def test_response_accepts_retains_and_dumps_unknown_fields() -> None:
    response = _Response.model_validate({"alarmRuleID": 123, "newVendorField": "future"})

    assert response.alarm_rule_id == 123
    assert response.model_extra == {"newVendorField": "future"}
    assert response.newVendorField == "future"
    assert response.model_dump() == {
        "alarm_rule_id": 123,
        "newVendorField": "future",
    }
    assert response.model_dump(by_alias=True) == {
        "alarmRuleID": 123,
        "newVendorField": "future",
    }


def test_response_validates_known_fields() -> None:
    with pytest.raises(ValidationError):
        _Response.model_validate({"alarmRuleID": "not-an-integer", "newVendorField": True})


def test_internal_accepts_known_fields() -> None:
    assert _Internal(value=1).value == 1


def test_internal_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        _Internal(value=1, unknown_field=True)


def test_models_are_frozen() -> None:
    model = _PlainModel(alarm_rule_id=123)

    with pytest.raises(ValidationError):
        model.alarm_rule_id = 456


def test_construction_is_keyword_only() -> None:
    assert _Request(value=1).value == 1

    with pytest.raises(TypeError):
        _Request(1)


def test_enum_members_are_retained() -> None:
    model = _EnumModel(state="active")

    assert model.state is _State.ACTIVE


def test_utc_datetime_is_accepted_and_remains_aware() -> None:
    occurred_at = datetime(2026, 8, 10, 13, tzinfo=UTC)

    model = _DatetimeModel(occurred_at=occurred_at)

    assert model.occurred_at == occurred_at
    assert model.occurred_at.tzinfo is not None
    assert model.occurred_at.utcoffset() == timedelta(0)


def test_non_utc_datetime_is_normalized_to_utc() -> None:
    occurred_at = datetime(2026, 8, 10, 15, tzinfo=timezone(timedelta(hours=2)))

    model = _DatetimeModel(occurred_at=occurred_at)

    assert model.occurred_at == datetime(2026, 8, 10, 13, tzinfo=UTC)
    assert model.occurred_at.tzinfo is UTC


def test_naive_datetime_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _DatetimeModel(occurred_at=datetime(2026, 8, 10, 13))


@pytest.mark.parametrize(
    ("model_class", "invalid_data", "sdk_error_type"),
    [
        (_Request, {"value": "invalid"}, RequestValidationError),
        (_Response, {"alarmRuleID": "invalid"}, ResponseValidationError),
    ],
)
def test_foundation_exposes_native_pydantic_validation_errors(
    model_class: type[SdkModel],
    invalid_data: dict[str, str],
    sdk_error_type: type[Exception],
) -> None:
    with pytest.raises(ValidationError) as exc_info:
        model_class.model_validate(invalid_data)

    assert not isinstance(exc_info.value, sdk_error_type)
