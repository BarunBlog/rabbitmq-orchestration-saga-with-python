import aio_pika
import os

_connection = None
_channel = None

async def connect_rabbit():
    global _connection, _channel

    if _connection is None or _connection.is_closed:
        print("[RabbitMQ] Connecting to RabbitMQ...", flush=True)

        try:
            _connection = await aio_pika.connect_robust(os.environ.get("RABBITMQ_URL"))
            _channel = await _connection.channel()

            print("[RabbitMQ] Connected to RabbitMQ...", flush=True)
        except Exception as e:
            print(f"[ERROR] Failed to connect to RabbitMQ: {e}", flush=True)

    return _channel


async def publish_message(exchange: str, routing_key: str, message: str):
    # print(f"[RabbitMQ] Preparing to publish to exchange '{exchange}' with routing key '{routing_key}'", flush=True)

    channel = await connect_rabbit()

    try:
        # Declare or create the exchange if needed.
        exchange_obj = await channel.declare_exchange(name=exchange, type=aio_pika.ExchangeType.DIRECT, durable=True)

        # Publish the message to the exchange with the routing key
        await exchange_obj.publish(
            message=aio_pika.Message(body=message.encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
            routing_key=routing_key
        )

        print(f"Message published to exchange '{exchange}' with routing key '{routing_key}': {message}", flush=True)
    except Exception as e:
        print(f"[ERROR] Failed to publish message: {e}", flush=True)