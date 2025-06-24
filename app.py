from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)

@app.route("/")
def home():
    return '''
    <html>
    <head>
        <title>Article Explorer</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <h1>Article Explorer</h1>
        <form action="/view" method="get">
            <label>Wikipedia URL:</label>
            <input type="url" name="q" placeholder="https://en.wikipedia.org/wiki/Cat" required>
            <button type="submit">View</button>
        </form>
    </body>
    </html>
    '''

@app.route("/view")
def view_article():
    url = request.args.get("q")
    if not url or "wikipedia.org" not in urlparse(url).netloc:
        return "Invalid or missing Wikipedia URL", 400

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")

        heading = soup.select_one("h1#firstHeading")
        content = soup.select_one("#mw-content-text")
        if not heading or not content:
            return "Could not extract content", 500

        # Remove infobox if present
        infobox = content.select_one(".infobox")
        if infobox:
            infobox.decompose()

        # Fix relative image and link URLs
        for tag in content.find_all(["img", "a"]):
            if tag.name == "img" and tag.has_attr("src") and tag["src"].startswith("/"):
                tag["src"] = "https://en.wikipedia.org" + tag["src"]
            elif tag.name == "a" and tag.has_attr("href") and tag["href"].startswith("/"):
                tag["href"] = "https://en.wikipedia.org" + tag["href"]

        return render_template("viewer.html", title=heading.text, heading=heading.text, content=str(content))

    except Exception as e:
        return f"Failed to fetch article: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
