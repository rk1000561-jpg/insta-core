import os
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

BASE_API = "https://instagraminfo.anshapi.workers.dev/info?username="

# requests.Session() use karne se connection open rehta hai, baar-baar naya connection nahi banana padta (Speed badhegi)
session = requests.Session()
session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
)


@app.route("/")
def home():
    return jsonify({"owner": "R3XTRON", "status": "running"})


@app.route("/api")
def instagram_lookup():  # Async hata diya taaki Vercel par crash na ho
    username = request.args.get("username", "").replace("@", "").strip().lower()

    if not username:
        return jsonify({"success": False, "error": "username required"}), 400

    try:
        # Timeout ko 8 seconds rakha hai taaki Vercel ke 10s limit se pehle hum apna error handle kar lein
        response = session.get(f"{BASE_API}{username}", timeout=8)

        if response.status_code != 200:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"upstream api failed with status {response.status_code}",
                    }
                ),
                500,
            )

        data = response.json()

        if not data or "username" not in data:
            return (
                jsonify({"success": False, "error": "profile not found"}),
                404,
            )

        return jsonify(
            {
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
                    "profile_image": data.get("profile_image"),
                },
            }
        )

    except requests.exceptions.Timeout:
        return (
            jsonify({"success": False, "error": "upstream api took too long"}),
            504,
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Vercel ko batane ke liye ki app yahi hai
app = app
