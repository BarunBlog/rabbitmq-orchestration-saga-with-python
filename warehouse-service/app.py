import json
import aio_pika
import asyncio
from rabbitmq import connect_rabbit, publish_message

async def process_warehouse_deduct_callback(body: bytes):
    data = eval(body.decode())
    print(f"[WAREHOUSE] Received 'warehouse.initiate' event: {data}", flush=True)

    # Simulate inventory deduction...
    data['inventory_status'] = 'deducted'
    print(f"[WAREHOUSE] Inventory deducted for order: {data}", flush=True)

    # Send the message to the Orchestrator
    exchange = "orchestrator_exchange"
    routing_key = "warehouse.deducted"

    # Publish payment completion data to the exchange
    await publish_message(exchange=exchange, routing_key=routing_key, message=json.dumps(data))

    print(f"[Warehouse] Sent warehouse inventory deducted message to Orchestrator. message: {data}", flush=True)


async def consume_warehouse_initiate_message():
    channel = await connect_rabbit()

    exchange = "warehouse_exchange"
    queue = "warehouse.warehouse.initiate.queue"
    routing_key = "warehouse.initiate"

    try:
        # Declare or create the exchange if needed.
        exchange = await channel.declare_exchange(name=exchange, type=aio_pika.ExchangeType.DIRECT, durable=True)

        # Declare or create the queue if needed.
        queue = await channel.declare_queue(queue, durable=True)

        # Bind the queue to the specified exchange
        await queue.bind(exchange, routing_key)

        print(f"[Warehouse] Waiting for messages in queue '{queue}'...", flush=True)

        # Start consuming
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        await process_warehouse_deduct_callback(message.body)
                    except Exception as e:
                        print(f"[ERROR] Failed to process message: {e}")

    except Exception as e:
        print(f"[ERROR] Failed to consume message: {e}", flush=True)


if __name__ == "__main__":
    asyncio.run(consume_warehouse_initiate_message())