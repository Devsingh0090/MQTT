from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
import uuid
import time
import threading

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
        client.publish(MQTT_TOPIC, message, qos=0)
        # QoS 0 is fire-and-forget; count as sent immediately
        return True, "Message published successfully"
    except Exception as e:
        return False, str(e)


# Background publisher control
publisher_thread = None
publisher_lock = threading.Lock()
stop_event = threading.Event()
current_message = ''
seq = 0
sent_count = 0
attempted_count = 0

def publisher_loop(message, interval_ms=200):
    global seq, sent_count, current_message
    current_message = message
    interval = interval_ms / 1000.0
    print(f"[publisher] loop start: interval_ms={interval_ms}, interval_s={interval}")
    while not stop_event.is_set():
        seq += 1
        payload = f"{message} {seq}"
        success, resp = publish_message(payload)
        if success:
            sent_count = seq          # seq == number of sends so far
            if seq % 10 == 0:
                print(f"[publisher] sent seq={seq}")
        else:
            print(f"[publisher] error at seq={seq}:", resp)
        stop_event.wait(interval)


@app.route('/publisher_app/start', methods=['POST'])
def start_publisher():
    global publisher_thread, seq, sent_count, current_message
    data = request.get_json(force=True) or {}
    message = data.get('message', '').strip()
    interval_ms = int(data.get('interval_ms', 200)) if data.get('interval_ms') is not None else 200
    if not message:
        return jsonify({'status': 'error', 'message': 'Message cannot be empty'}), 400

    if publisher_thread and publisher_thread.is_alive():
        return jsonify({'status': 'error', 'message': 'Publisher already running'}), 400

    stop_event.clear()
    seq = 0
    sent_count = 0
    print(f"[publisher] starting with interval_ms={interval_ms}")
    current_message = message
    publisher_thread = threading.Thread(target=publisher_loop, args=(message, interval_ms), daemon=True)
    publisher_thread.start()
    return jsonify({'status': 'ok', 'message': 'started'})


@app.route('/publisher_app/stop', methods=['POST'])
def stop_publisher():
    global publisher_thread
    if not (publisher_thread and publisher_thread.is_alive()):
        return jsonify({'status': 'error', 'message': 'Publisher not running'}), 400
    stop_event.set()
    publisher_thread.join(timeout=5)
    publisher_thread = None
    return jsonify({'status': 'ok', 'sent_count': sent_count})


@app.route('/publisher_app/status')
def publisher_status():
    running = bool(publisher_thread and publisher_thread.is_alive())
    return jsonify({'running': running, 'sent_count': sent_count})


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




