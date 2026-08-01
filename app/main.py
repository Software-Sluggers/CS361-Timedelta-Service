import re
from datetime import datetime, timedelta
from typing import Annotated, Literal

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import AfterValidator, BaseModel

app = FastAPI(
    title="Timedelta Service",
    version="0.1.0",
)

Operation = Literal["add"]
Unit = Literal["days", "hours", "minutes", "seconds"]

ERROR_MESSAGES = {
    "timestamp": (
        "Invalid timestamp. The timestamp must be an ISO-formatted timestamp."
    ),
    "operation": "Invalid operation. Currently, only add is supported.",
    "value": "Invalid value. The value must be an integer.",
    "unit": "Invalid unit. The unit must be one of days, hours, minutes, or seconds.",
}


def validate_timestamp(timestamp: str) -> str:
    """Ensure the query timestamp is valid ISO-8601."""

    if not re.search(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\dZ$", timestamp):
        raise ValueError(ERROR_MESSAGES["timestamp"])
    return timestamp


Timestamp = Annotated[str, AfterValidator(validate_timestamp)]


class TimedeltaResponse(BaseModel):
    """Result of adding a duration to a timestamp."""

    OriginalTimestamp: str
    Value: int
    Unit: Unit
    ResultingTimestamp: str
    Summary: str


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    _request: Request,
    exception: RequestValidationError,
) -> JSONResponse:
    """Return a readable response for invalid timedelta requests."""

    for error in exception.errors():
        location = error.get("loc", ())
        for field, message in ERROR_MESSAGES.items():
            if field in location:
                return JSONResponse(
                    status_code=400,
                    content={"Error": message},
                )

    return JSONResponse(
        status_code=400,
        content={"Error": "Invalid request."},
    )


def format_timestamp(timestamp: datetime) -> str:
    """Format a datetime as an ISO UTC timestamp with millisecond precision."""

    milliseconds = timestamp.microsecond // 1000
    return timestamp.strftime("%Y-%m-%dT%H:%M:%S.") + f"{milliseconds:03d}Z"


def build_summary(
    value: int,
    unit: Unit,
    original_timestamp: str,
    resulting_timestamp: str,
) -> str:
    """Build a human-readable description of the timedelta result."""

    if value < 0:
        return (
            f"{abs(value)} {unit} before {original_timestamp} is {resulting_timestamp}"
        )

    return f"{value} {unit} after {original_timestamp} is {resulting_timestamp}"


def apply_timedelta(
    timestamp: str,
    value: int,
    unit: Unit,
) -> TimedeltaResponse:
    """Add a duration to a timestamp and return the full response body."""

    original = datetime.fromisoformat(timestamp)
    resulting = original + timedelta(**{unit: value})
    resulting_timestamp = format_timestamp(resulting)

    return TimedeltaResponse(
        OriginalTimestamp=timestamp,
        Value=value,
        Unit=unit,
        ResultingTimestamp=resulting_timestamp,
        Summary=build_summary(
            value,
            unit,
            timestamp,
            resulting_timestamp,
        ),
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    """Confirm that the service is running."""

    return {"status": "ok"}


@app.get("/timedelta", response_model=TimedeltaResponse)
def create_timedelta(
    timestamp: Annotated[Timestamp, Query(...)],
    operation: Annotated[Operation, Query(...)],
    value: Annotated[int, Query(...)],
    unit: Annotated[Unit, Query(...)],
) -> TimedeltaResponse:
    """Add a duration to the supplied timestamp."""

    return apply_timedelta(timestamp, value, unit)
