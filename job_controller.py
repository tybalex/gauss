import asyncio
import nats
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError

import logging
import argparse
import uuid

from kubernetes import client
from kubernetes import config
from kubernete_job import KubernetesJob

logging.basicConfig(level=logging.INFO)
config.load_kube_config()

async def create_job_controller():
    # It is very likely that the demo server will see traffic from clients other than yours.
    # To avoid this, start your own locally and modify the example to use it.
    nc = await nats.connect("nats://localhost:4222")

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("create job: '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))

    # Simple publisher and async subscriber via coroutine.
    sub = await nc.subscribe("create_job", cb=message_handler)


async def delete_job_controller():
    # It is very likely that the demo server will see traffic from clients other than yours.
    # To avoid this, start your own locally and modify the example to use it.
    nc = await nats.connect("nats://localhost:4222")

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("delete job: '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))

    # Simple publisher and async subscriber via coroutine.
    sub = await nc.subscribe("delete_job", cb=message_handler)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(create_job_controller(), delete_job_controller()))
    try:
        loop.run_forever()
    finally:
        loop.close()