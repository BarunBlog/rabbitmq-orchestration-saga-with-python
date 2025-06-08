import json
from rabbitmq import connect_rabbit

def process_payment_callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"[PAYMENT] Received 'payment.initiate' event: {data}", flush=True)

    # Simulate payment processing...
    data['payment_status'] = 'paid'
    print(f"[PAYMENT] Payment processed: {data}", flush=True)

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

def consume_payment_initiate_message():
    connection, channel = connect_rabbit()

    exchange = "payment_exchange"
    queue = "payment.payment.initiate.queue"
    routing_key = "payment.initiate"

    try:
        # Declare or create the exchange if needed.
        channel.exchange_declare(exchange=exchange, exchange_type='direct', durable=True)

        # Declare or create the queue if needed.
        channel.queue_declare(queue=queue, durable=True)

        # Bind the queue to the specified exchange
        channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)

        print(f"[Payment] Waiting for messages in queue '{queue}'...", flush=True)

        # Start consuming
        channel.basic_consume(queue=queue, on_message_callback=process_payment_callback)
        channel.start_consuming()

    except Exception as e:
        print(f"[ERROR] Failed to consume message: {e}", flush=True)
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()


if __name__ == "__main__":
    consume_payment_initiate_message()