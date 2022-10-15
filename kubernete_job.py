import logging
import argparse
import uuid

from kubernetes import client
from kubernetes import config

logging.basicConfig(level=logging.INFO)
config.load_kube_config()


class KubernetesJob:
    def __init__(self):

        # Init Kubernetes
        self.core_api = client.CoreV1Api()
        self.batch_api = client.BatchV1Api()

    def create_namespace(self, namespace):

        namespaces = self.core_api.list_namespace()
        all_namespaces = []
        for ns in namespaces.items:
            all_namespaces.append(ns.metadata.name)

        if namespace in all_namespaces:
            logging.debug(f"Namespace {namespace} already exists. Reusing.")
        else:
            namespace_metadata = client.V1ObjectMeta(name=namespace)
            self.core_api.create_namespace(
                client.V1Namespace(metadata=namespace_metadata)
            )
            logging.debug(f"Created namespace {namespace}.")

        return namespace

    @staticmethod
    def create_container(image, name, pull_policy, args=""):

        container = client.V1Container(
            image=image,
            name=name,
            image_pull_policy=pull_policy,
            args=[args],
            command=["python3", "./run.py"],
        )

        logging.debug(
            f"Created container with name: {container.name}, "
            f"image: {container.image} and args: {container.args}"
        )

        return container

    @staticmethod
    def create_pod_template(pod_name, container):
        pod_template = client.V1PodTemplateSpec(
            spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
            metadata=client.V1ObjectMeta(name=pod_name, labels={"pod_name": pod_name}),
        )

        return pod_template

    @staticmethod
    def create_job(job_name, pod_template):
        metadata = client.V1ObjectMeta(name=job_name, labels={"job_name": job_name})

        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=metadata,
            spec=client.V1JobSpec(backoff_limit=0, template=pod_template),
        )

        return job
    

if __name__ == "__main__":
    k8s = KubernetesJob()
    