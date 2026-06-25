import httpx
from flask import Flask, jsonify, request

app = Flask(__name__)

BASE_API = "https://instagraminfo.anshapi.workers.dev/info?username="

# Ek permanent Async Client banayenge speed boost ke liye
# Aur realistic User-Agent headers taaki upstream API block na kare
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}
async_client = httpx.AsyncClient(headers=HEADERS, timeout=15.0)


@app.route("/")
def home():
    return jsonify({"owner": "R3XTRON", "status": "running"})


# Route ko ASYNC banaya taaki ye background mein wait kare, server ko block na kare
@app.route("/api")
async def instagram_lookup():
    username = request.args.get("username", "").replace("@", "").strip().lower()

    if not username:
        return jsonify({"success": False, "error": "username required"}), 400

    try:
        # requests.get ki jagah async_client.get use kiya
        response = await async_client.get(f"{BASE_API}{username}")

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

        # Kuch APIs success response mein bhi error details deti hain, usko handle kiya
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

    except httpx.TimeoutException:
        return (
            jsonify({"success": False, "error": "upstream api timeout (slow)"}),
            504,
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Application close hote waqt client ko clean tarike se band karne ke liye
@app.teardown_appcontext
async def shutdown_session(exception=None):
    # Safe shutdown for async client
    pass


if __name__ == "__main__":
    # Flask ko async support ke sath chalane ke liye asgiref ya hypercorn lagta hai,
    # par modern Flask (2.0+) internally async functions ko handle kar leta hai.
    app.run(debug=True)
