from flask import Flask, request, jsonify
import json
import time
import os
import uuid

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
    keys = load_keys()
    new_key = {
        "serial": str(uuid.uuid4()).upper(),
        "expires_at": time.time() + (60 * 60 * 24 * 30),  # 30 days
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
            if key["device_id"] is None:
                key["device_id"] = device_id
                save_keys(keys)
                return jsonify({
                    "success": True,
                    "message": "Serial activated for this device",
                    "expires_at": key["expires_at"]
                })
            elif key["device_id"] == device_id:
                return jsonify({
                    "success": True,
                    "message": "Serial valid for this device",
                    "expires_at": key["expires_at"]
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Serial already used on another device"
                }), 403
    return jsonify({"success": False, "message": "Invalid serial"}), 404

@app.route('/delete', methods=['POST'])
def delete_key():
    data = request.get_json()
    serial = data.get('serial')
    
    if not serial:
        return jsonify({"success": False, "message": "Missing serial"}), 400
        
    keys = load_keys()
    new_keys = [k for k in keys if k["serial"] != serial]
    
    if len(new_keys) != len(keys):
        save_keys(new_keys)
        return jsonify({"success": True, "message": "Serial deleted"})
    return jsonify({"success": False, "message": "Serial not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)