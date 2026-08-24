from flask import Flask, request, jsonify
from pathlib import Path
from urllib.parse import parse_qsl
from datetime import datetime, timezone
import hashlib
import hmac
import json

from config import BOT_TOKEN
from database.keys_db import get_key_by_value

app = Flask(__name__)

INIT_DATA_MAX_AGE = 300  # 5 minutes


def verify_telegram_init_data(init_data: str):
    if not init_data:
        return None, "Missing Telegram initData"

    try:
        pairs = dict(parse_qsl(init_data, keep_blank_values=True))
        received_hash = pairs.pop("hash", None)

        if not received_hash:
            return None, "Missing Telegram initData hash"

        auth_date = pairs.get("auth_date")
        if not auth_date:
            return None, "Missing auth_date"

        now = int(datetime.now(timezone.utc).timestamp())

        try:
            if now - int(auth_date) > INIT_DATA_MAX_AGE:
                return None, "Telegram session data expired"
        except ValueError:
            return None, "Invalid auth_date"

        data_check_string = "\n".join(
            f"{key}={value}"
            for key, value in sorted(pairs.items())
        )

        secret_key = hmac.new(
            b"WebAppData",
            BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()

        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(calculated_hash, received_hash):
            return None, "Invalid Telegram authentication"

        user_raw = pairs.get("user")
        if not user_raw:
            return None, "Telegram user data missing"

        user = json.loads(user_raw)
        user_id = user.get("id")

        if not user_id:
            return None, "Telegram user ID missing"

        return int(user_id), None

    except (ValueError, TypeError, json.JSONDecodeError):
        return None, "Invalid Telegram authentication data"
    except Exception:
        return None, "Authentication failed"


@app.post("/api/verify-key")
def verify_key():
    body = request.get_json(silent=True) or {}

    init_data = body.get("initData", "")
    access_key = body.get("key", "").strip()

    if not access_key:
        return jsonify({
            "success": False,
            "code": "KEY_REQUIRED",
            "message": "Please enter your access key."
        }), 400

    user_id, error = verify_telegram_init_data(init_data)

    if error:
        return jsonify({
            "success": False,
            "code": "TELEGRAM_AUTH_FAILED",
            "message": error
        }), 401

    key_data = get_key_by_value(access_key)

    if not key_data:
        return jsonify({
            "success": False,
            "code": "INVALID_KEY",
            "message": "Invalid access key."
        }), 403

    if key_data["user_id"] != user_id:
        return jsonify({
            "success": False,
            "code": "KEY_USER_MISMATCH",
            "message": "This key belongs to another Telegram account."
        }), 403

    if key_data["key_status"] != "Active":
        status = key_data["key_status"]

        if status == "Expired":
            message = "Your access key has expired."
        else:
            message = "Your access key is inactive."

        return jsonify({
            "success": False,
            "code": "KEY_NOT_ACTIVE",
            "message": message
        }), 403

    expire_time = key_data.get("expire_time")

    if not expire_time:
        return jsonify({
            "success": False,
            "code": "KEY_NO_EXPIRY",
            "message": "This access key has no active expiry."
        }), 403

    if expire_time <= datetime.now():
        return jsonify({
            "success": False,
            "code": "KEY_EXPIRED",
            "message": "Your access key has expired."
        }), 403

    return jsonify({
        "success": True,
        "message": "Access verified.",
        "user_id": user_id,
        "expires_at": expire_time.isoformat(),
        "plan_name": key_data.get("plan_name")
    }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
