import json
import aio_pika
import asyncio
from rabbitmq import connect_rabbit, publish_message, consume_message

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


async def main():
    await connect_rabbit()
    await asyncio.gather(
        consume_message(exchange="warehouse_exchange", queue="warehouse.warehouse.initiate.queue", routing_key="warehouse.initiate", handler=process_warehouse_deduct_callback)
    )

if __name__ == "__main__":
    asyncio.run(main())