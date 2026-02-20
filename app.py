from flask import Flask, render_template, request, jsonify
import paho.mqtt.publish as publish

# Publisher Flask app: sends user messages to MQTT topic
# MQTT broker settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "print/topic"

app = Flask(__name__)


@app.route('/publisher_app/')
def index():
    # Show UI with text input and Send button at URL ending with the app name
    return render_template('index.html')


@app.route('/publisher_app/send', methods=['POST'])
def send_message():
    # Receive JSON payload from frontend and publish to MQTT
    data = request.get_json(force=True)
    message = data.get('message', '')

    try:
        # Publish a single message to the MQTT broker
        # paho-mqtt provides a convenience function publish.single()
        publish.single(MQTT_TOPIC, payload=message, hostname=MQTT_BROKER, port=MQTT_PORT)
        return jsonify({'status': 'ok', 'message': 'Message sent to printer queue'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    # Run the Flask development server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)

