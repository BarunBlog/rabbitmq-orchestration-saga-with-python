import asyncio
import json
from rabbitmq import connect_rabbit, publish_message, consume_message


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


async def main():
    await connect_rabbit()
    await asyncio.gather(
        consume_message(exchange="order_exchange", queue="orchestrator.order.created.queue", routing_key="order.created", handler=process_order_callback),
        consume_message(exchange="payment_exchange", queue="orchestrator.payment.completed.queue", routing_key="payment.completed", handler=process_payment_completed_callback),
        consume_message(exchange="orchestrator_exchange", queue="orchestrator.warehouse.deducted.queue", routing_key="warehouse.deducted", handler=process_warehouse_deducted_callback),
    )

if __name__ == "__main__":
    asyncio.run(main())


