from flask import Flask, request, render_template, jsonify
from sentiment_analysis import scrape_comments
import os;

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Gets the path of `sentiment_an`
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")  # Correct template folder path
STATIC_DIR = os.path.join(BASE_DIR, "static")  # If you have a static folder
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    instagram_url = request.form["instagram_url"]
    comments = scrape_comments(instagram_url)

    if not comments:
        return jsonify({"error": "Failed to fetch comments. Instagram may have blocked access."})

    return jsonify(comments)

if __name__ == "__main__":
    app.run(debug=True, port=5055)
