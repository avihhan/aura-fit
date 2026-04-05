"""Shared helpers used across routes and services."""

from flask import g


PLATFORM_TENANT_ID = 1


def current_tenant_id() -> int:
    """Return the tenant_id for the current request user."""
    return g.tenant_id


def current_user_id() -> int:
    """Return the user_id for the current request user."""
    return g.user_id
