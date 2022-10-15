import logging
import uuid

from kubernetes import client
from kubernetes import config
from kubernete_job import KubernetesJob

logging.basicConfig(level=logging.INFO)
config.load_kube_config()

def parse_v1job_status(result): 
    """
    refer to https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1JobStatus.md
    """
    if result.status.succeeded:
        return "succeess"
    elif result.status.failed:
        return "failed"
    elif result.status.active:
        return "active"
    else: return "inprogress"


def get_jobs():
    batch_api = client.BatchV1Api()
    _namespace = "default"
    result = batch_api.list_namespaced_job(_namespace)
    return result


def list_all_job():
    result = get_jobs()
    res = [r.metadata.name for r in result.items]
    return res

def delete_job(job_name):
    batch_api = client.BatchV1Api()
    _namespace = "default"
    try:
        if job_name in list_all_job():
            result = batch_api.delete_namespaced_job(job_name, _namespace)
            return 0, f"job deleted. details : {result.status}"
        else:
            return 1, "no such training job."
    except Exception as e:
        logging.warning(e)
        return 2, "exception deletion."


def get_job_status(job_name):
    batch_api = client.BatchV1Api()
    _namespace = "default"
    try:
        result = batch_api.read_namespaced_job_status(job_name, _namespace)
        return parse_v1job_status(result)
    except Exception as e:
        logging.warning(e)
        return f"failed to get job status: {job_name}"

def create_new_job(job_name, image_name=None):

    """ Steps 1 to 3 is the equivalent of the ./manifestfiles/shuffler_job.yaml """

    # Kubernetes instance
    k8s = KubernetesJob()
    if not image_name:
        _image = "docker.io/tybalex/opni-gauss:dev"
    else :
        _image = image_name

    # STEP1: CREATE A CONTAINER
    
    _name = "ml-training" if "training" in job_name else "ml-inferencing"
    _pull_policy = "Always"
    shuffler_container = k8s.create_container(_image, _name, _pull_policy)

    # STEP2: CREATE A POD TEMPLATE SPEC
    _pod_name = f"pod-{job_name}"
    _pod_spec = k8s.create_pod_template(_pod_name, shuffler_container)

    # STEP3: CREATE A JOB
    _job = k8s.create_job(job_name, _pod_spec)

    # STEP4: CREATE NAMESPACE
    _namespace = "default"
    k8s.create_namespace(_namespace)

    # STEP5: EXECUTE THE JOB
    batch_api = client.BatchV1Api()
    batch_api.create_namespaced_job(_namespace, _job)

    return job_name

if __name__ == "__main__":
    create_new_job("test123",)
    # result = get_jobs()
    # res = [r.metadata.name  for r in result.items if r.status.active]
    # print(res)