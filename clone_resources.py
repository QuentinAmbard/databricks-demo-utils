from utils import copy_jobs, copy_dashboard, copy_dlt_pipeline
from utils.client import Client
import json


def get_client():
    with open("secret.json", "r") as r:
        secret = json.loads(r.read())
        source = Client(secret["source"]["url"], secret["source"]["token"])
        targets = []
        for target in secret["targets"]:
            target = Client(target["url"], target["token"], target["data_source_id"])
            targets.append(target)
        return source, targets


source_client, target_clients = get_client()
for target_client in target_clients:
    copy_dashboard.clone_dashboards_with_tags(source_client, target_client, ["field_demos"])
    copy_jobs.clone_jobs_starting_with(source_client, target_client, "field_demo")
    #copy_dlt_pipeline.clone_pipelines_starting_with(source_client, dest_client, "field_demo")