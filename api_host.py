import logging
from fastapi import FastAPI
import subprocess
import uuid
import json

from kubernetes import client
from kubernetes_apis import *

import asyncio
import nats
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/get_job_status/{job_name}")
async def get_training_jobs(job_name):
    # TODO: show progress. that would be helpful.
    result = get_job_status(job_name)
    return {"message": result}


@app.get("/delete_job/{job_name}")
async def delete_training_jobs(job_name):
    nc = await nats.connect("nats://localhost:4222")
    await nc.publish("delete_job", job_name.encode())
    return {"message": f"deletion of job : {job_name} submitted."}


@app.get("/create_job")
async def create_job():
    # job_name = create_new_job()
    job_id = str(uuid.uuid4())
    _name = "ml-training"
    job_name = f"{_name}-{job_id}"
    nc = await nats.connect("nats://localhost:4222")
    await nc.publish("create_job", job_name.encode())
    return {"message" : f"job creation request submitted, job-name : {job_name}"}



@app.get("/list_jobs")
async def list_jobs():
    job_names = list_all_job()
    return {"message" : f"all jobs : {job_names}"}










