from flask import Flask, jsonify
import json

app = Flask(__name__)

def load_serials():
    with open("serials.json", "r") as f:
        return json.load(f)

def save_serials(serials):
    with open("serials.json", "w") as f:
        json.dump(serials, f, indent=2)

@app.route("/")
def home():
    return "Butterfly Serial API is working!"

@app.route("/getkey")
def get_key():
    serials = load_serials()
    for s in serials:
        if not s["used"]:
            s["used"] = True
            save_serials(serials)
            return jsonify({"serial": s["key"]})
    return jsonify({"error": "No serials left"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
