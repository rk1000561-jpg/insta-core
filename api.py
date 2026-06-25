import os
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Base API worker URL
BASE_URL = "https://instagraminfo.anshapi.workers.dev"

# Professional session setup taaki baar-baar connection banana na pade aur response fast aaye
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
})

# Helper function jo common request handle karega aur code chota rakhega
def fetch_from_upstream(endpoint, username):
    try:
        response = session.get(f"{BASE_URL}/{endpoint}?username={username}", timeout=8)
        
        if response.status_code != 200:
            return {
                "success": False, 
                "error": f"Upstream API failed with status {response.status_code}"
            }, response.status_code
            
        data = response.json()
        return {"success": True, "data": data}, 200
        
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Upstream API took too long to respond"}, 504
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@app.route("/")
def home():
    return jsonify({
        "owner": "R3XTRON",
        "status": "running",
        "available_endpoints": {
            "/api/info": "Get basic profile info",
            "/api/posts": "Get latest 12 posts",
            "/api/reels": "Get latest reels",
            "/api/stories": "Get active stories"
        }
    })

# 1. PROFILE INFO ENDPOINT
@app.route("/api/info")
def instagram_info():
    username = request.args.get("username", "").replace("@", "").strip().lower()
    if not username:
        return jsonify({"success": False, "error": "username required"}), 400
        
    result, status_code = fetch_from_upstream("info", username)
    return jsonify(result), status_code

# 2. LATEST POSTS ENDPOINT
@app.route("/api/posts")
def instagram_posts():
    username = request.args.get("username", "").replace("@", "").strip().lower()
    if not username:
        return jsonify({"success": False, "error": "username required"}), 400
        
    result, status_code = fetch_from_upstream("posts", username)
    return jsonify(result), status_code

# 3. REELS ENDPOINT
@app.route("/api/reels")
def instagram_reels():
    username = request.args.get("username", "").replace("@", "").strip().lower()
    if not username:
        return jsonify({"success": False, "error": "username required"}), 400
        
    result, status_code = fetch_from_upstream("reels", username)
    return jsonify(result), status_code

# 4. STORIES ENDPOINT
@app.route("/api/stories")
def instagram_stories():
    username = request.args.get("username", "").replace("@", "").strip().lower()
    if not username:
        return jsonify({"success": False, "error": "username required"}), 400
        
    result, status_code = fetch_from_upstream("stories", username)
    return jsonify(result), status_code


# Vercel deployment support
app = app
