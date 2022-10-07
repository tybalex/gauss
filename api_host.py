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
    result = get_job_status(job_name)
    return {"message": result}


@app.get("/delete_job/{job_name}")
async def delete_training_jobs(job_name):
    result = delete_job(job_name)
    nc = await nats.connect("nats://localhost:4222")
    await nc.publish("delete_job", job_name.encode())
    return {"message": result}


@app.get("/create_job")
async def create_job():
    job_name = create_new_job()
    nc = await nats.connect("nats://localhost:4222")
    await nc.publish("create_job", job_name.encode())
    return {"message" : f"created job : {job_name}"}



@app.get("/list_jobs")
async def list_jobs():
    job_names = list_all_job()
    return {"message" : f"all jobs : {job_names}"}










