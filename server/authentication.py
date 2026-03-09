from functools import wraps

import jwt as pyjwt
from flask import Blueprint, current_app, g, jsonify, request
from supabase import Client, create_client

bp = Blueprint("auth", __name__)


# ---------------------------------------------------------------------------
# Supabase client helper
# ---------------------------------------------------------------------------

def get_supabase_admin() -> Client:
    """Return a Supabase client authenticated with the service-role key."""
    return create_client(
        current_app.config["SUPABASE_URL"],
        current_app.config["SUPABASE_SERVICE_ROLE_KEY"],
    )


# ---------------------------------------------------------------------------
# Auth middleware
# ---------------------------------------------------------------------------

def require_auth(f):
    """Verify Supabase JWT and attach user/tenant context to flask.g."""

    @wraps(f)
    def decorated(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header"}), 401

        token = header.removeprefix("Bearer ")

        try:
            jwks_url = current_app.config["SUPABASE_URL"] + "/auth/v1/.well-known/jwks.json"
            jwks_client = pyjwt.PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            payload = pyjwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256"],
                audience="authenticated",
            )
        except pyjwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except pyjwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        auth_uid = payload.get("sub")
        if not auth_uid:
            return jsonify({"error": "Token missing sub claim"}), 401

        sb = get_supabase_admin()
        result = (
            sb.table("users")
            .select("id, tenant_id, role, email")
            .eq("auth_id", auth_uid)
            .maybe_single()
            .execute()
        )

        if not result.data:
            return jsonify({"error": "User not found"}), 401

        g.auth_uid = auth_uid
        g.user_id = result.data["id"]
        g.tenant_id = result.data["tenant_id"]
        g.role = result.data["role"]
        g.email = result.data["email"]

        return f(*args, **kwargs)

    return decorated


def require_role(*allowed_roles):
    """Must be applied after @require_auth so g.role is set."""

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if g.get("role") not in allowed_roles:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)

        return decorated

    return decorator


@bp.route("/signup", methods=["POST"])
def signup():
    body = request.get_json(silent=True) or {}
    email = body.get("email", "").strip()
    password = body.get("password", "")
    tenant_id = body.get("tenant_id")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400
    if not tenant_id:
        return jsonify({"error": "tenant_id is required"}), 400

    sb = get_supabase_admin()

    tenant = (
        sb.table("tenants")
        .select("id")
        .eq("id", tenant_id)
        .maybe_single()
        .execute()
    )
    if not tenant or not tenant.data:
        return jsonify({"error": "Invalid tenant_id"}), 400

    try:
        auth_resp = sb.auth.admin.create_user(
            {
                "email": email,
                "password": password,
                "email_confirm": True,
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    auth_user = auth_resp.user
    if not auth_user:
        return jsonify({"error": "Signup failed"}), 500

    sb.table("users").insert(
        {
            "auth_id": str(auth_user.id),
            "tenant_id": tenant_id,
            "email": email,
            "password_hash": "managed-by-supabase-auth",
            "role": "member",
            "is_email_verified": True,
        }
    ).execute()

    sign_in = sb.auth.sign_in_with_password(
        {"email": email, "password": password}
    )

    return jsonify(
        {
            "access_token": sign_in.session.access_token,
            "refresh_token": sign_in.session.refresh_token,
            "user": {
                "auth_id": str(auth_user.id),
                "email": email,
                "tenant_id": tenant_id,
                "role": "member",
            },
        }
    ), 201


@bp.route("/login", methods=["POST"])
def login():
    body = request.get_json(silent=True) or {}
    email = body.get("email", "").strip()
    password = body.get("password", "")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    sb = get_supabase_admin()

    try:
        auth_resp = sb.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception:
        return jsonify({"error": "Invalid email or password"}), 401

    if not auth_resp.session:
        return jsonify({"error": "Invalid email or password"}), 401

    auth_uid = str(auth_resp.user.id)

    user_row = (
        sb.table("users")
        .select("id, tenant_id, role, email")
        .eq("auth_id", auth_uid)
        .maybe_single()
        .execute()
    )

    if not user_row.data:
        return jsonify({"error": "User profile not found"}), 404

    tenant_row = (
        sb.table("tenants")
        .select("id, name, logo_url, primary_color, secondary_color")
        .eq("id", user_row.data["tenant_id"])
        .maybe_single()
        .execute()
    )

    return jsonify(
        {
            "access_token": auth_resp.session.access_token,
            "refresh_token": auth_resp.session.refresh_token,
            "user": user_row.data,
            "tenant": tenant_row.data if tenant_row.data else None,
        }
    )


@bp.route("/refresh", methods=["POST"])
def refresh():
    body = request.get_json(silent=True) or {}
    refresh_token = body.get("refresh_token", "")

    if not refresh_token:
        return jsonify({"error": "refresh_token is required"}), 400

    sb = get_supabase_admin()

    try:
        resp = sb.auth._refresh_access_token(refresh_token)
    except Exception:
        return jsonify({"error": "Unable to refresh session"}), 401

    if not resp.session:
        return jsonify({"error": "Unable to refresh session"}), 401

    return jsonify(
        {
            "access_token": resp.session.access_token,
            "refresh_token": resp.session.refresh_token,
        }
    )


@bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    sb = get_supabase_admin()
    try:
        sb.auth.admin.sign_out(g.auth_uid)
    except Exception:
        pass
    return jsonify({"message": "Logged out"}), 200


@bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    body = request.get_json(silent=True) or {}
    email = body.get("email", "").strip()

    if not email:
        return jsonify({"error": "email is required"}), 400

    sb = get_supabase_admin()
    try:
        sb.auth.reset_password_email(email)
    except Exception:
        pass

    return jsonify({"message": "If that email exists, a reset link has been sent"}), 200
