import asyncio
import nats
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError

import logging
import argparse
import uuid

from kubernetes import client
from kubernetes import config
from kubernete_job import KubernetesJob
from kubernetes_apis import create_new_job, delete_job

logging.basicConfig(level=logging.INFO)
config.load_kube_config()


cancle_pool = set()

async def create_job_controller():
    # It is very likely that the demo server will see traffic from clients other than yours.
    # To avoid this, start your own locally and modify the example to use it.
    nc = await nats.connect("nats://localhost:4222")

    async def message_handler(msg):
        subject = msg.subject
        job_name = msg.data.decode()
        if job_name in cancle_pool:
            cancle_pool.discard(job_name)
            logging.info(f"canceled job : {job_name}")
        else:
            create_new_job(job_name, image_name="docker.io/tybalex/opni-gauss:dev")
            logging.info("created job: '{subject}': {data}".format(
                subject=subject,  data=job_name))
        

    # Simple publisher and async subscriber via coroutine.
    sub = await nc.subscribe("create_job", cb=message_handler)


async def delete_job_controller():
    # It is very likely that the demo server will see traffic from clients other than yours.
    # To avoid this, start your own locally and modify the example to use it.
    nc = await nats.connect("nats://localhost:4222")

    async def message_handler(msg):
        subject = msg.subject
        job_name = msg.data.decode()
        status_code, desc = delete_job(job_name)
        if status_code == 0:
            pass
        elif status_code == 1:
            cancle_pool.add(job_name)
        logging.info(desc)
        logging.info("deleted job: '{subject}': {data}".format(
            subject=subject, data=job_name))

    # Simple publisher and async subscriber via coroutine.
    sub = await nc.subscribe("delete_job", cb=message_handler)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(create_job_controller(), delete_job_controller()))
    try:
        loop.run_forever()
    finally:
        loop.close()