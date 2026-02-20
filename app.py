from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
import uuid

MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "myhome/sensor1"

app = Flask(__name__)

def publish_message(message):
    try:
        client_id = f"publisher-{uuid.uuid4()}"
        client = mqtt.Client(client_id=client_id)

        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(MQTT_TOPIC, message, qos=0)
        client.disconnect()

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

    success, response_message = publish_message(message)

    if success:
        return jsonify({'status': 'ok', 'message': response_message})
    else:
        return jsonify({'status': 'error', 'message': response_message}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
