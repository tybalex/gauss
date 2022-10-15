import asyncio
import time
import nats
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError

import logging
import argparse
import uuid

from kubernetes import client
from kubernetes import config
from kubernete_job import KubernetesJob
from kubernetes_apis import create_new_job, delete_job, get_job_status, get_jobs

logging.basicConfig(level=logging.INFO)
config.load_kube_config()

INFERENCING_JOB_NAME = "ml-inferencing"


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
            logging.info(f"[job creator] -- canceled job : {job_name}")
        else:
            res = get_active_job()
            if len(res) > 0:
                if INFERENCING_JOB_NAME in res[0]:
                    delete_job(res[0])
                    logging.info(f"[job creator] -- switch inferencing job {res[0]} to training job...")
                elif "training" in res[0]:
                    while (len(res) > 0 and "training" in res[0]):
                        logging.info(f"[job creator] -- waiting on previous training job : {res[0]}")
                        await asyncio.sleep(30)
                        res = get_active_job()
            create_new_job(job_name, image_name="docker.io/tybalex/opni-gauss:training")
            logging.info("[job creator] -- created job: '{subject}': {data}".format(
                subject=subject,  data=job_name))
            while (job_status:=get_job_status(job_name) == "active" or job_status=="inprogress"):
                logging.info(f"[job creator] -- current job active : {job_name}")
                await asyncio.sleep(60)
            logging.info(f"[job creator] -- job {job_name} complated, status : {get_job_status(job_name)}")
        

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


def get_active_job():
    result = get_jobs()
    res = [r.metadata.name  for r in result.items if r.status.active]
    return res

async def job_maintainer():
    while True:
        logging.info("[job maintainer] -- checking status...")
        res = get_active_job()
        if len(res) == 0: # no job at all, launch an inferencing job
            logging.info("[job maintainer] no job running -- launching a inferencing job")
            create_new_job(INFERENCING_JOB_NAME, image_name="docker.io/tybalex/opni-gauss:inferencing")
        else:
            logging.info(f"[job maintainer] -- a job is running : {res[0]}")
        # other cases: if there's training on inferencing job, do nothing
        await asyncio.sleep(60)





if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(create_job_controller(), delete_job_controller(), job_maintainer()))
    try:
        loop.run_forever()
    finally:
        loop.close()