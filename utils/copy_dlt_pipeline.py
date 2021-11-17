import requests
import json
from utils.client import Client

def delete_pipelines(client: Client, name_prefix):
    assert len(name_prefix) > 2
    print(f"delete existing pipeline starting with {name_prefix}")
    for p in get_all_pipelines(client, name_prefix):
        print(f"deleting pipeline {p['pipeline_id']} - {p['name']}")
        requests.delete(client.url+"/api/2.0/pipelines/"+p["pipeline_id"], headers = client.headers).json()

def get_all_pipelines(client: Client, name_prefix = ""):
    page_size = 100
    def get_all(pipelines, page):
        r = requests.get(client.url+"/api/2.0/pipelines", headers = client.headers, json = {"filter": f"name LIKE '{name_prefix}%'"}).json()
        if "statuses" in r:
            pipelines.extend(r["statuses"])
            if len(r["statuses"]) >= page_size:
                pipelines = get_all(pipelines, page + 1)
        return pipelines
    return get_all([], 1)

def clone_pipelines(source_client: Client, target_client: Client, pipelines):
    new_pipelines = []
    for p in pipelines:
        p = requests.get(source_client.url+"/api/2.0/pipelines/"+p["pipeline_id"], headers = source_client.headers).json()
        print(p)
        del p["spec"]["id"]
        new_p = requests.post(target_client.url + "/api/2.0/pipelines", headers = target_client.headers, json = p["spec"]).json()
        print(new_p)
        new_pipelines.append(new_p["pipeline_id"])
    return new_pipelines

def launch_pipelines(client: Client, pipelines_id):
    for id in pipelines_id:
        print(f"starting pipeline id={id}")
        p = requests.post(client.url+"/api/2.0/pipelines/"+id+"/updates", headers = client.headers).json()
        print(p)

def delete_and_copy_pipelines_starting_with(source_client: Client, target_query: Client, prefixes):
    #Todo could do something more efficient by pushes a list of prefix in the functions instead
    for prefix in prefixes:
        assert len(prefix) > 1
        delete_pipelines(target_query, prefix)
        #get the pipelines to clone from the source
        pipelines_to_clone = get_all_pipelines(source_client, prefix)
        #re-create the pipelines:
        clones_id = clone_pipelines(source_client, target_query, pipelines_to_clone)
        #and run them to warm them up
        launch_pipelines(target_query, clones_id)

