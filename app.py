from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
import uuid
import time

MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "myhome/sensor1"

app = Flask(__name__)

# ---- Create Global MQTT Client ----
client_id = f"publisher-{uuid.uuid4()}"
client = mqtt.Client(client_id=client_id)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)

client.on_connect = on_connect
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()  # Important (background thread start)

# -------------------------------------

def publish_message(message):
    try:
        result = client.publish(MQTT_TOPIC, message, qos=0)
        result.wait_for_publish()   # ensure publish completed
        return True, "Message published successfully"
    except Exception as e:
        return False, str(e)


@app.route('/publisher_app/')
def index():
    return render_template('index.html')


@app.route('/publisher_app/send', methods=['POST'])
def send_message():
    data = request.get_json(force=True)
    message = data.get('message', '')

    if not message:
        return jsonify({'status': 'error', 'message': 'Message cannot be empty'}), 400

    start_time = time.time()
    success, response_message = publish_message(message)
    end_time = time.time()

    print("Publish Time:", (end_time - start_time) * 1000, "ms")

    if success:
        return jsonify({'status': 'ok', 'message': response_message})
    else:
        return jsonify({'status': 'error', 'message': response_message}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
