# import paho.mqtt.client as mqtt
# import time
# import json

# broker = "broker.hivemq.com"
# port = 1883
# topic = "aman/print/test1"

# client = mqtt.Client()
# client.connect(broker, port)

# while True:
#     data = {
#         "name": "Aman Store",
#         "item": "Milk",
#         "price": 25
#     }

#     client.publish(topic, json.dumps(data))
#     print("Message Sent")
#     time.sleep(10)
