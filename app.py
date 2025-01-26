from flask import Flask, render_template, jsonify, request, Response
import random
import time
import json
import os
from flask_socketio import SocketIO
import eventlet
import csv
import datetime
from flask_cors import CORS  # For handling cross-origin requests

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS)

# In-memory store for demonstration purposes
message_history = []

@app.route('/rockblock', methods=['POST'])
def handle_rockblock():
    imei = request.args.get('imei')
    username = request.args.get('username')
    password = request.args.get('password')

    # Validate credentials
    if imei != "300434065264590" or username != "myUser" or password != "myPass":
        return "FAILED,10,Invalid login credentials", 400

    # Extract and decode data
    data = request.args.get('data')
    if not data:
        return "FAILED,16,No data provided", 400

    try:
        decoded_message = bytes.fromhex(data).decode('utf-8')
    except ValueError:
        return "FAILED,14,Could not decode hex data", 400

    # Parse decoded message
    try:
        message_parts = dict(part.split(":") for part in decoded_message.split(","))
        message = message_parts.get("message", "No message provided")
        timestamp = datetime.datetime.utcnow().isoformat()

        # Append to history
        message_history.append({
            "message": message,
            "timestamp": timestamp
        })

        print(f"Message: {message}, Timestamp: {timestamp}")
    except Exception as e:
        print("Error parsing message:", e)
        return "FAILED,15,Error parsing message data", 400

    return "OK,0"

@app.route('/live-data', methods=['GET'])
def live_data():
    """
    Fetch the latest message.
    """
    if message_history:
        return jsonify(message_history[-1])  # Return the latest data
    return jsonify({})

@app.route('/history', methods=['GET'])
def load_flight_history():
    """
    Fetch all historical messages.
    """
    return jsonify(message_history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Make sure to deploy with the correct URL on Render


