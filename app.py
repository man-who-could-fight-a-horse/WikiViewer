from flask import Flask, request, Response, send_from_directory
import requests
import os

app = Flask(__name__, static_folder="static")

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route("/")
def serve_index():
    return send_from_directory("static", "index.html")

@app.route("/get", methods=["GET", "OPTIONS"])
def proxy():
    if request.method == "OPTIONS":
        return Response(status=204)
        
    target_url = request.args.get("q")
    if not target_url:
        return "Missing 'url' parameter", 400

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(target_url, headers=headers, timeout=10)
        return Response(r.content, content_type=r.headers.get("Content-Type", "text/html"))
    except requests.exceptions.RequestException as e:
        return f"Failed to fetch: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)