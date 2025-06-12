import aio_pika
import asyncio
import json
from rabbitmq import connect_rabbit, publish_message


async def process_order_callback(body: bytes):
    order_data = eval(body.decode())

    print(f"[Orchestrator] Received 'order.created' event: {order_data}", flush=True)

    # Initiate the payment from orchestrator
    await initiate_payment(order_data)

async def process_payment_completed_callback(body: bytes):

    payment_data = eval(body.decode())

    print(f"[Orchestrator] Received 'payment.completed' event: {payment_data}", flush=True)

    await initiate_warehouse(payment_data)

async def process_warehouse_deducted_callback(body: bytes):
    warehouse_data = eval(body.decode())
    print(f"[Orchestrator] Received 'warehouse.deducted' event: {warehouse_data}", flush=True)


async def consume_order_create_message():
    _, channel = await connect_rabbit()

    exchange = "order_exchange"
    queue = "orchestrator.order.created.queue"
    routing_key = "order.created"

    try:
        # Declare or create the exchange if needed.
        exchange = await channel.declare_exchange(name=exchange, type=aio_pika.ExchangeType.DIRECT, durable=True)

        # Declare or create the queue if needed.
        queue = await channel.declare_queue(queue, durable=True)

        # Bind the queue to the specified exchange
        await queue.bind(exchange, routing_key)

        print(f"[Orchestrator] Waiting for messages in queue '{queue}'...", flush=True)

        # Start consuming
        # await queue.consume(process_order_callback)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        await process_order_callback(message.body)
                    except Exception as e:
                        print(f"[ERROR] Failed to process message: {e}")
    except Exception as e:
        print(f"[ERROR] Failed to consume message: {e}", flush=True)


async def initiate_payment(order: dict):
    exchange = "payment_exchange"
    routing_key = "payment.initiate"

    payment_data = {
        "order_uuid": order["order_uuid"],
        "amount": 1000, # used static value
        "payment_status": "pending"
    }

    await publish_message(exchange=exchange, routing_key=routing_key, message=json.dumps(payment_data))

    print(f"[Orchestrator] Sent payment initiation message: {payment_data}", flush=True)


async def consume_payment_completed_message():
    _, channel = await connect_rabbit()

    exchange = "payment_exchange"
    queue = "orchestrator.payment.completed.queue"
    routing_key = "payment.completed"

    try:
        # Declare or create the exchange if needed.
        exchange = await channel.declare_exchange(name=exchange, type=aio_pika.ExchangeType.DIRECT, durable=True)

        # Declare or create the queue if needed.
        queue = await channel.declare_queue(queue, durable=True)

        # Bind the queue to the specified exchange
        await queue.bind(exchange, routing_key)

        print(f"[Orchestrator] Waiting for messages in queue '{queue}'...", flush=True)

        # Start consuming
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        await process_payment_completed_callback(message.body)
                    except Exception as e:
                        print(f"[ERROR] Failed to process message: {e}")

    except Exception as e:
        print(f"[ERROR] Failed to consume message: {e}", flush=True)


async def initiate_warehouse(payment: dict):
    exchange = "warehouse_exchange"
    routing_key = "warehouse.initiate"

    warehouse_data = {
        "order_uuid": payment["order_uuid"],
        "item_id": "ITEM123",  # used static data
        "quantity": 1, # # used static data
    }

    # Publish warehouse data to the exchange
    await publish_message(exchange=exchange, routing_key=routing_key, message=json.dumps(warehouse_data))

    print(f"[Orchestrator] Sent warehouse initiation message: {warehouse_data}", flush=True)

async def consume_warehouse_deducted_message():
    _, channel = await connect_rabbit()

    exchange = "orchestrator_exchange"
    queue = "orchestrator.warehouse.deducted.queue"
    routing_key = "warehouse.deducted"

    try:
        # Declare or create the exchange if needed.
        exchange = await channel.declare_exchange(name=exchange, type=aio_pika.ExchangeType.DIRECT, durable=True)

        # Declare or create the queue if needed.
        queue = await channel.declare_queue(queue, durable=True)

        # Bind the queue to the specified exchange
        await queue.bind(exchange, routing_key)

        print(f"[Orchestrator] Waiting for messages in queue '{queue}'...", flush=True)

        # Start consuming
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        await process_warehouse_deducted_callback(message.body)
                    except Exception as e:
                        print(f"[ERROR] Failed to process message: {e}")

    except Exception as e:
        print(f"[ERROR] Failed to consume message: {e}", flush=True)


async def main():
    await asyncio.gather(
        consume_order_create_message(),
        consume_payment_completed_message(),
        consume_warehouse_deducted_message(),
    )

if __name__ == "__main__":
    asyncio.run(main())


