from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__, template_folder="web/templates", static_folder="web/static")

def get_latest_data():
    conn = sqlite3.connect("cloud_cover.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM observations ORDER BY timestamp DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return dict(row) if row else {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    return jsonify(get_latest_data())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)