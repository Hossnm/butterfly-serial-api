from flask import Flask, jsonify
import uuid
import json
import time
import os

app = Flask(__name__)
DATA_FILE = "keys.json"
EXPIRY_DAYS = 30

def load_keys():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_keys(keys):
    with open(DATA_FILE, "w") as f:
        json.dump(keys, f, indent=2)

def clean_expired_keys(keys):
    now = time.time()
    return [key for key in keys if now < key["expires_at"]]

@app.route("/getkey")
def get_key():
    keys = load_keys()
    keys = clean_expired_keys(keys)
    new_key = str(uuid.uuid4()).upper()
    expiry = time.time() + (EXPIRY_DAYS * 86400)
    keys.append({"key": new_key, "expires_at": expiry})
    save_keys(keys)
    return jsonify({"serial": new_key, "expires_at": expiry})

@app.route("/validate/<key>")
def validate_key(key):
    keys = load_keys()
    keys = clean_expired_keys(keys)
    save_keys(keys)
    for entry in keys:
        if entry["key"] == key:
            return jsonify({"valid": True, "expires_at": entry["expires_at"]})
    return jsonify({"valid": False}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)