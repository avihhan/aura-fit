from flask import Blueprint, jsonify, request

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["POST"])
def login():
    # TODO: validate body, call Supabase Auth or verify token
    return jsonify({"message": "Auth not implemented yet"}), 501


@bp.route("/refresh", methods=["POST"])
def refresh():
    return jsonify({"message": "Refresh not implemented yet"}), 501
