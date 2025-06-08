import json
from rabbitmq import connect_rabbit, publish_message


def process_order_callback(ch, method, properties, body):
    order_data = json.loads(body)
    print(f"[Orchestrator] Received 'order.created' event: {order_data}", flush=True)

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # Initiate the payment from orchestrator
    initiate_payment(order_data)

def process_payment_completed_callback(ch, method, properties, body):
    payment_data = json.loads(body)
    print(f"[Orchestrator] Received 'payment.completed' event: {payment_data}", flush=True)

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

    initiate_warehouse(payment_data)




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

    # Publish payment data to the exchange
    publish_message(exchange=exchange, routing_key=routing_key, message=json.dumps(payment_data))

    print(f"[Orchestrator] Sent payment initiation message: {payment_data}", flush=True)


def consume_payment_completed_message():
    connection, channel = connect_rabbit()

    exchange = "payment_exchange"
    queue = "orchestrator.payment.completed.queue"
    routing_key = "payment.completed"

    try:
        # Declare or create the exchange if needed.
        channel.exchange_declare(exchange=exchange, exchange_type='direct', durable=True)

        # Declare or create the queue if needed.
        channel.queue_declare(queue=queue, durable=True)

        # Bind the queue to the specified exchange
        channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)

        print(f"[Orchestrator] Waiting for messages in queue '{queue}'...", flush=True)

        # Start consuming
        channel.basic_consume(queue=queue, on_message_callback=process_payment_completed_callback)
        channel.start_consuming()

    except Exception as e:
        print(f"[ERROR] Failed to consume message: {e}", flush=True)
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()


def initiate_warehouse(payment: dict):
    exchange = "warehouse_exchange"
    routing_key = "warehouse.initiate"

    warehouse_data = {
        "order_uuid": payment["order_uuid"],
        "item_id": "ITEM123",  # used static data
        "quantity": 1, # # used static data
    }

    # Publish warehouse data to the exchange
    publish_message(exchange=exchange, routing_key=routing_key, message=json.dumps(warehouse_data))

    print(f"[Orchestrator] Sent warehouse initiation message: {warehouse_data}", flush=True)

if __name__ == "__main__":
    # Used tread to run in parallel
    from threading import Thread

    Thread(target=consume_order_create_message).start()
    Thread(target=consume_payment_completed_message).start()


