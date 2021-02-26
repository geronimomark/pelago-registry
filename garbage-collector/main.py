import os
import json
import requests

URL = os.getenv('REGISTRY_URL', 'https://localhost:30007')
CREDS = os.getenv('REGISTRY_CREDS', '12345')

def list_repositories():
    url = URL + '/v2/_catalog'
    headers = {'Authorization': 'Basic ' + CREDS}
    response = requests.get(url, headers=headers, verify=False)
    return json.loads(response.text)

def list_tags(repository):
    url = URL + f"/v2/{repository}/tags/list"
    headers = {'Authorization': 'Basic ' + CREDS}
    response = requests.get(url, headers=headers, verify=False)
    return json.loads(response.text)

def get_manifest(repository, tag):
    url = URL + f"/v2/{repository}/manifests/{tag}"
    headers = {
        'Authorization': 'Basic ' + CREDS,
        'Accept': 'application/vnd.docker.distribution.manifest.v2+json'
    }
    response = requests.get(url, headers=headers, verify=False)
    return response.headers

def delete_tag(repository, manifest):
    url = URL + f"/v2/{repository}/manifests/{manifest}"
    headers = {
        'Authorization': 'Basic ' + CREDS,
        'Accept': 'application/vnd.docker.distribution.manifest.v2+json'
    }
    return requests.delete(url, headers=headers, verify=False)

def main():
    with open('delete-policy.json') as json_file:
        delete_policy = json.load(json_file)
    repositories = list_repositories()
    for repository in repositories["repositories"]:
        print(f"{repository}")
        tmp_delete_policy = delete_policy["default"]
        if repository in delete_policy:
            tmp_delete_policy = delete_policy[repository] - 1
        tags = list_tags(repository)
        # TODO here, sort tags by latest created
        # not yet available in registry API
        # tag = sort_by_latest(tags)
        if tmp_delete_policy < len(tags):
            ctr = 0
            for tag in tags["tags"]:
                print(f"  {tag}")
                if ctr > tmp_delete_policy:
                    manifest = get_manifest(repository, tag)
                    print(f"Deleting {repository}:{tag} with hash {manifest}")
                    delete_response = delete_tag(repository, manifest["Docker-Content-Digest"])
                    # do something w/ delete_response
                    # retry if needed
                ctr = ctr + 1

main()
