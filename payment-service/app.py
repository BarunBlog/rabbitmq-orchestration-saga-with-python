import aio_pika
import asyncio
import json
from rabbitmq import connect_rabbit, publish_message

async def process_payment_callback(body: bytes):
    str_data = body.decode()
    dict_data = eval(str_data)
    print(f"[PAYMENT] Received 'payment.initiate' event: {dict_data}", flush=True)

    # Simulate payment processing...
    dict_data['payment_status'] = 'paid'
    print(f"[PAYMENT] Payment processed: {dict_data}", flush=True)

    # Send the message to the Orchestrator
    exchange = "payment_exchange"
    routing_key = "payment.completed"

    # Publish payment completion data to the exchange
    await publish_message(exchange=exchange, routing_key=routing_key, message=json.dumps(dict_data))

    print(f"[Payment] Sent payment completion message to Orchestrator. message: {dict_data}", flush=True)

async def consume_payment_initiate_message():
    _, channel = await connect_rabbit()

    exchange = "payment_exchange"
    queue = "payment.payment.initiate.queue"
    routing_key = "payment.initiate"

    try:
        # Declare or create the exchange if needed.
        exchange = await channel.declare_exchange(name=exchange, type=aio_pika.ExchangeType.DIRECT, durable=True)

        # Declare or create the queue if needed.
        queue = await channel.declare_queue(queue, durable=True)

        # Bind the queue to the specified exchange
        await queue.bind(exchange, routing_key)

        print(f"[Payment] Waiting for messages in queue '{queue}'...", flush=True)

        # Start consuming
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        await process_payment_callback(message.body)
                    except Exception as e:
                        print(f"[ERROR] Failed to process message: {e}")

    except Exception as e:
        print(f"[ERROR] Failed to consume message: {e}", flush=True)


if __name__ == "__main__":
    asyncio.run(consume_payment_initiate_message())