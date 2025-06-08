import json
from rabbitmq import connect_rabbit, publish_message


def process_order_callback(ch, method, properties, body):
    order_data = json.loads(body)
    print(f"[Orchestrator] Received 'order.created' event: {order_data}", flush=True)

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # Initiate the payment from orchestrator
    initiate_payment(order_data)



def consume_order_create_message():
    connection, channel = connect_rabbit()

    exchange = "order_exchange"
    queue = "orchestrator.order.created.queue"
    routing_key = "order.created"

    try:
        # Declare or create the exchange if needed.
        channel.exchange_declare(exchange=exchange, exchange_type='direct', durable=True)

        # Declare or create the queue if needed.
        channel.queue_declare(queue=queue, durable=True)

        # Bind the queue to the specified exchange
        channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)

        print(f"[Orchestrator] Waiting for messages in queue '{queue}'...", flush=True)

        # Start consuming
        channel.basic_consume(queue=queue, on_message_callback=process_order_callback)
        channel.start_consuming()
    except Exception as e:
        print(f"[ERROR] Failed to consume message: {e}", flush=True)
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()


def initiate_payment(order: dict):
    exchange = "payment_exchange"
    routing_key = "payment.initiate"

    payment_data = {
        "order_uuid": order["order_uuid"],
        "amount": 1000, # used static value
        "payment_status": "pending"
    }

    print(f"[Orchestrator] Sent payment initiation message: {payment_data}", flush=True)

    # Publish payment data to the exchange
    publish_message(exchange=exchange, routing_key=routing_key, message=json.dumps(payment_data))

if __name__ == "__main__":
    consume_order_create_message()


