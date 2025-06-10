from flask import Flask, request, jsonify
import json
import time
import os

app = Flask(__name__)
KEYS_FILE = 'keys.json'

def load_keys():
    if not os.path.exists(KEYS_FILE):
        return []
    with open(KEYS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

@app.route('/getkey', methods=['GET'])
def get_key():
    import uuid
    keys = load_keys()
    new_key = {
        "serial": str(uuid.uuid4()).upper(),
        "expires_at": time.time() + (60 * 60 * 24 * 30),  # 30 days from now
        "device_id": None
    }
    keys.append(new_key)
    save_keys(keys)
    return jsonify(new_key)

@app.route('/verify', methods=['POST'])
def verify_key():
    data = request.get_json()
    serial = data.get('serial')
    device_id = data.get('device_id')

    if not serial or not device_id:
        return jsonify({"success": False, "message": "Missing serial or device ID"}), 400

    keys = load_keys()
    for key in keys:
        if key["serial"] == serial:
            if time.time() > key["expires_at"]:
                return jsonify({"success": False, "message": "Serial expired"}), 403
            if key["device_id"] is None:
                key["device_id"] = device_id
                save_keys(keys)
                return jsonify({"success": True, "message": "Serial activated for this device"})
            elif key["device_id"] == device_id:
                return jsonify({"success": True, "message": "Serial valid for this device"})
            else:
                return jsonify({"success": False, "message": "Serial already used on another device"}), 403
    return jsonify({"success": False, "message": "Invalid serial"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
