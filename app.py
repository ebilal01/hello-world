from flask import Flask, render_template, jsonify, request
import datetime
from flask_cors import CORS  # For handling cross-origin requests
import json
import csv
from flask import Response
import struct

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS)

# In-memory store for demonstration purposes
message_history = []

@app.route('/')
def index():
    return render_template('index.html')

import json

@app.route('/rockblock', methods=['POST'])
def handle_rockblock():
    imei = request.args.get('imei')
    data = request.args.get('data')

    # Debugging: Log incoming request
    print(f"Received POST /rockblock - IMEI: {imei}, Data: {data}")

    if imei != "300434065264590":
        print("Invalid credentials")
        return "FAILED,10,Invalid login credentials", 400

    if not data:
        print("No data provided")
        return "FAILED,16,No data provided", 400

    try:
        byte_data = bytearray.fromhex(data)

        if len(byte_data) != 50:  # Ensure 50 bytes as expected
            print(f"Unexpected message length: {len(byte_data)} bytes")
            return "FAILED,17,Invalid message length", 400

        # Unpack binary data into meaningful values
        unpacked_data = struct.unpack('IhffHhhhhhhhhhhhhhhhh', byte_data)
        unpacked_data = list(unpacked_data)

        # Scale values where necessary
        for x in range(5, 12):  # Pressure and temperatures (multiplied by 10 before sending)
            unpacked_data[x] /= 10
        for x in range(12, 15):  # Average velocities (multiplied by 1000 before sending)
            unpacked_data[x] /= 1000
        for x in range(15, 21):  # Std and peak velocities (multiplied by 100 before sending)
            unpacked_data[x] /= 100

        # Convert Unix Epoch timestamp to UTC format
        sent_time_utc = datetime.datetime.fromtimestamp(unpacked_data[0], datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')

        # Store data for live retrieval
        message_data = {
            "received_time": datetime.datetime.utcnow().isoformat() + "Z",
            "sent_time": sent_time_utc,
            "unix_epoch": unpacked_data[0],
            "siv": unpacked_data[1],
            "latitude": unpacked_data[2],
            "longitude": unpacked_data[3],
            "altitude": unpacked_data[4],
            "pressure_mbar": unpacked_data[5],
            "temperature_pht_c": unpacked_data[6],
            "temperature_cj_c": unpacked_data[7],
            "temperature_tctip_c": unpacked_data[8],
            "roll_deg": unpacked_data[9],
            "pitch_deg": unpacked_data[10],
            "yaw_deg": unpacked_data[11],
            "vavg_1_mps": unpacked_data[12],
            "vavg_2_mps": unpacked_data[13],
            "vavg_3_mps": unpacked_data[14],
            "vstd_1_mps": unpacked_data[15],
            "vstd_2_mps": unpacked_data[16],
            "vstd_3_mps": unpacked_data[17],
            "vpk_1_mps": unpacked_data[18],
            "vpk_2_mps": unpacked_data[19],
            "vpk_3_mps": unpacked_data[20],
        }

        # Append to history
        message_history.append(message_data)

        # Debugging: Confirm message was saved
        print(f"Processed and stored message: {message_data}")

        return "OK,0"

    except Exception as e:
        print("Error processing data:", e)
        return "FAILED,15,Error processing message data", 400


@app.route('/live-data', methods=['GET'])
def get_live_data():
    return jsonify(message_history[-1] if message_history else {"message": "No data received yet"})

@app.route('/history', methods=['GET'])
def load_flight_history():
    """
    Fetch all historical messages.
    """
    return jsonify(message_history)

@app.route('/download-history', methods=['GET'])
def download_history():
    if not message_history:
        return "No data available", 404

    def generate_csv():
        fieldnames = message_history[0].keys()
        yield ','.join(fieldnames) + '\n'  # Header row
        for row in message_history:
            yield ','.join(str(row[field]) for field in fieldnames) + '\n'  # Data rows

    return Response(generate_csv(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment; filename=flight_history.csv"})

@app.route('/message-history', methods=['GET'])
def message_history_endpoint():
    return jsonify(message_history) if message_history else jsonify([])


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Use Render's assigned port
    app.run(host='0.0.0.0', port=port) # Make sure to deploy with the correct URL on Render




