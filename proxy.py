from flask import Flask, request, Response, send_from_directory
import requests
import os

app = Flask(__name__, static_folder="static")

@app.route("/")
def index():
    # Serve your HTML file
    return send_from_directory(app.static_folder, "index.html")

@app.route("/proxy", methods=["GET", "OPTIONS"])
def proxy():
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
        return "", 204, headers

    target_url = request.args.get("url")
    if not target_url:
        return "Missing url parameter", 400

    try:
        resp = requests.get(target_url, stream=True)
    except requests.exceptions.RequestException as e:
        return f"Error fetching target URL: {e}", 500

    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [(name, value) for name, value in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    headers.append(("Access-Control-Allow-Origin", "*"))
    headers.append(("Access-Control-Allow-Methods", "GET, OPTIONS"))
    headers.append(("Access-Control-Allow-Headers", "Content-Type"))

    return Response(resp.raw, status=resp.status_code, headers=headers)

if __name__ == "__main__":
    app.run(port=8080)
