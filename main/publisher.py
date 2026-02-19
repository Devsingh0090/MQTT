import paho.mqtt.client as mqtt
import time
import json
import argparse

broker = "broker.hivemq.com"
port = 1883
topic = "aman/print/test1"


def main():
    parser = argparse.ArgumentParser(description="MQTT publisher for printing tests")
    parser.add_argument("-n", "--name", help="Name field to send")
    parser.add_argument("-i", "--item", help="Item field to send")
    parser.add_argument("-p", "--price", type=float, help="Price field to send")
    parser.add_argument("-t", "--interval", type=float, default=10, help="Publish interval in seconds")
    args = parser.parse_args()

    client = mqtt.Client()
    client.connect(broker, port)

    try:
        # If all three fields provided via CLI, publish that repeatedly
        if args.name is not None and args.item is not None and args.price is not None:
            data = {"name": args.name, "item": args.item, "price": args.price}
            print(f"Publishing fixed message every {args.interval} seconds: {data}")
            while True:
                client.publish(topic, json.dumps(data))
                print("Message Sent:", data)
                time.sleep(args.interval)

        # Otherwise enter interactive mode for ad-hoc messages
        else:
            print("Interactive mode. Press Ctrl+C to exit.")
            while True:
                try:
                    name = input("Name: ").strip()
                    item = input("Item: ").strip()
                    price_s = input("Price: ").strip()
                    price = float(price_s)
                except ValueError:
                    print("Invalid price — please enter a number.")
                    continue

                data = {"name": name, "item": item, "price": price}
                client.publish(topic, json.dumps(data))
                print("Message Sent:", data)
                time.sleep(args.interval)

    except KeyboardInterrupt:
        print("Exiting publisher")
    finally:
        try:
            client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    main()
