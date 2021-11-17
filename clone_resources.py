from utils import copy_jobs, copy_dashboard, copy_dlt_pipeline
from utils.client import Client
import json


def get_client():
    with open("config.json", "r") as r:
        secret = json.loads(r.read())
        source = Client(secret["source"]["url"], secret["source"]["token"], job_prefixes = secret["source"]["job_prefixes"],
                        dlt_prefixes = secret["source"]["dlt_prefixes"], dashboard_tags = secret["source"]["dashboard_tags"])
        targets = []
        for target in secret["targets"]:
            client = Client(target["url"], target["token"], target["data_source_id"])
            if "sql_database_name" in target:
                client.sql_database_name = target["sql_database_name"]
            targets.append(client)
        return source, targets


source_client, target_clients = get_client()
for target_client in target_clients:
    #copy_dashboard.delete_and_clone_dashboards_with_tags(source_client, target_client, source_client.dashboard_tags)
    #copy_jobs.delete_and_clone_jobs_starting_with(source_client, target_client, source_client.job_prefixes)
    copy_dlt_pipeline.delete_and_copy_pipelines_starting_with(source_client, target_client, source_client.dlt_prefixes)