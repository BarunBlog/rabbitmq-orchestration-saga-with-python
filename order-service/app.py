import json
import uuid
from flask import Flask, request, jsonify
from rabbitmq import publish_message

app = Flask(__name__)

@app.route("/order", methods=["POST"])
def create_order():

    exchange = "order_exchange"
    routing_key = "order.created"

    try:
        print("Started processing the order", flush=True)

        # Simulating basic order data
        order = {
            "order_uuid": str(uuid.uuid4()),
            "status": "created"
        }

        # Send order data to orchestrator queue
        publish_message(exchange=exchange, routing_key=routing_key, message=json.dumps(order))

        return jsonify({"message": "Order created and event published", "order": order}), 201

    except Exception as e:
        print(f"[ERROR] Failed to create the order: {e}", flush=True)
        return jsonify({"message": "Failed to create the order"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)