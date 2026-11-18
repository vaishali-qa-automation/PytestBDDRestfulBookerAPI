"""
Reusable assertion helpers for API response validation.
Keeps step definitions clean — all assertion logic and error messaging lives here.
"""

from typing import Any
import jsonschema
from requests import Response

def assert_status_code(response: Response, expected: int) -> None:
    """
    Validates the HTTP status code.

    :param response: requests Response object
    :param expected: expected HTTP status code
    """
    actual = response.status_code
    assert actual == expected, (
        f"Expected status {expected}, got {actual}.\n"
        f"URL: {response.url}\n"
        f"Body: {response.text[:500]}"          # truncate to avoid flooding logs
    )

def assert_json_field_equals(response: Response, field: str, expected: Any) -> None:
    """
    Validates that a top-level JSON field has the expected value.

    :param response: requests Response object
    :param field: top-level key in the JSON body
    :param expected: expected value
    """
    body = _safe_json(response)
    actual = body.get(field)
    assert actual == expected, (
        f"Field '{field}': expected '{expected}', got '{actual}'.\n"
        f"Full body: {body}"
    )

def assert_json_contains_keys(response: Response, keys: list[str]) -> None:
    """
    Validates that the JSON body contains all expected top-level keys.

    :param response: requests Response object
    :param keys: list of keys that must be present
    """
    body = _safe_json(response)
    missing = [k for k in keys if k not in body]
    assert not missing, (
        f"Missing keys: {missing}.\n"
        f"Available keys: {list(body.keys())}\n"
        f"Full body: {body}"
    )

def assert_json_field_not_none(response: Response, field: str) -> None:
    """
    Validates that a top-level JSON field exists and is not None/null.

    :param response: requests Response object
    :param field: top-level key in the JSON body
    """
    body = _safe_json(response)
    value = body.get(field)
    assert value is not None, (
        f"Field '{field}' is None or missing.\n"
        f"Full body: {body}"
    )

def assert_response_time_below(response: Response, max_seconds: float) -> None:
    """
    Validates that the response was received within the time threshold.

    :param response: requests Response object
    :param max_seconds: maximum acceptable response time in seconds
    """
    actual = response.elapsed.total_seconds()
    assert actual < max_seconds, (
        f"Response took {actual:.3f}s, exceeded threshold of {max_seconds}s.\n"
        f"URL: {response.url}"
    )

def assert_json_list_not_empty(response: Response) -> None:
    """
    Validates that the response body is a non-empty JSON list.

    :param response: requests Response object
    """
    body = _safe_json(response)
    assert isinstance(body, list), (
        f"Expected a JSON list, got {type(body).__name__}.\n"
        f"Body: {body}"
    )
    assert len(body) > 0, "Expected non-empty list, got empty list."

def assert_matches_schema(response: Response, schema: dict) -> None:
    """
    Validates the JSON body against a JSON Schema definition.

    :param response: requests Response object
    :param schema: JSON Schema dict
    """
    body = _safe_json(response)
    try:
        jsonschema.validate(instance=body, schema=schema)
    except jsonschema.ValidationError as e:
        raise AssertionError(
            f"Schema validation failed: {e.message}\n"
            f"Path: {list(e.absolute_path)}\n"
            f"Body: {body}"
        ) from e

# ---------------------------------------------------------------------------
# Private helper
# ---------------------------------------------------------------------------

def _safe_json(response: Response) -> dict | list:
    """
    Safely parses JSON from a response, with a clear error if it fails.
    """
    try:
        return response.json()
    except Exception:
        raise AssertionError(
            f"Response body is not valid JSON.\n"
            f"Status: {response.status_code}\n"
            f"Body: {response.text[:500]}"
        )