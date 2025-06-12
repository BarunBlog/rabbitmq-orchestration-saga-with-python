import asyncio
import json
from rabbitmq import connect_rabbit, publish_message, consume_message

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


async def main():
    await connect_rabbit()
    await asyncio.gather(
        consume_message(exchange="payment_exchange", queue="payment.payment.initiate.queue", routing_key="payment.initiate", handler=process_payment_callback)
    )

if __name__ == "__main__":
    asyncio.run(main())