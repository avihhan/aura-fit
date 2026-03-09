from flask import Blueprint, jsonify

bp = Blueprint("users", __name__)


@bp.route("/me", methods=["GET"])
def me():
    # TODO: require auth, return current user from Supabase
    return jsonify({"message": "Requires auth"}), 401
