import requests
from utils.client import Client

def delete_jobs(client: Client, name_prefix):
    print(f"deleting all jobs starting with {name_prefix}...")
    assert len(name_prefix) > 2
    for j in get_all_jobs(client, name_prefix):
        print(f"deleting job {j['job_id']} - {j['settings']['name']}")
        requests.post(client.url+"/api/2.1/jobs/delete", headers = client.headers, json={"job_id": j["job_id"]}).json()

def get_all_jobs(client: Client, name_prefix = ""):
    page_size = 25
    def get_all(jobs, page):
        r = requests.get(client.url+"/api/2.1/jobs/list", headers = client.headers, json = {"limit": page_size, "offset": page*page_size}).json()
        if "jobs" in r:
            jobs.extend([j for j in r["jobs"] if j["settings"]["name"].startswith(name_prefix)])
            if len(r["jobs"]) >= page_size:
                jobs = get_all(jobs, page + 1)
        return jobs
    return get_all([], 0)

def clone_jobs(src_client: Client, target_client: Client, jobs):
    new_jobs = []
    for j in jobs:
        j = requests.get(src_client.url+"/api/2.1/jobs/get", headers = src_client.headers, json={"job_id": j["job_id"]}).json()
        new_j = requests.post(target_client.url+"/api/2.1/jobs/create", headers = target_client.headers, json = j["settings"]).json()
        print(f"new job cloned: {new_j}")
        new_jobs.append(new_j["job_id"])
    return new_jobs

def launch_pipelines(client: Client, pipelines_id):
    for id in pipelines_id:
        print(f"starting pipeline id={id}")
        p = requests.post(client.url+"/api/2.0/pipelines/"+id+"/updates", headers = client.headers).json()
        print(p)


def clone_jobs_starting_with(src_client: Client, target_client: Client, prefix):
    assert len(prefix) > 1
    #delete existing pipelines starting with "field_demos"
    delete_jobs(target_client, prefix)
    #get the pipelines to clone from the source
    print(f"fetching jobs to clone starting with {prefix}...")
    jobs_to_clone = get_all_jobs(src_client, prefix)
    #re-create the pipelines:
    clones_id = clone_jobs(src_client, target_client, jobs_to_clone)
    print(f"job cloned: {clones_id}")

