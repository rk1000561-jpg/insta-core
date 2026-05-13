from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

BASE_API = "https://instagraminfo.anshapi.workers.dev/info?username="

@app.route("/")
def home():
    return jsonify({
        "owner": "R3XTRON",
        "status": "running"
    })

@app.route("/api")
def instagram_lookup():
    username = request.args.get("username", "").replace("@", "").strip().lower()

    if not username:
        return jsonify({
            "success": False,
            "error": "username required"
        }), 400

    try:
        response = requests.get(
            f"{BASE_API}{username}",
            timeout=20
        )

        if response.status_code != 200:
            return jsonify({
                "success": False,
                "error": "upstream api failed"
            }), 500

        data = response.json()

        if not data or "username" not in data:
            return jsonify({
                "success": False,
                "error": "profile not found"
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "username": data.get("username"),
                "full_name": data.get("full_name"),
                "id": data.get("id"),
                "followers": data.get("followers"),
                "following": data.get("following"),
                "bio": data.get("bio"),
                "is_private": data.get("is_private"),
                "is_verified": data.get("is_verified"),
                "profile_image": data.get("profile_image")
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


app = app
